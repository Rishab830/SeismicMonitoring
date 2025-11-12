import seisbench.models as sbm
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import json
import base64
import io
from kafka import KafkaProducer
from datetime import datetime
import sys
import os
import time

class SeismicDataProducer:
    def __init__(self, kafka_bootstrap_servers='kafka-service:9092'):
        self.client = Client("IRIS")
        self.model = sbm.PhaseNet.from_pretrained("original")
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            max_request_size=10485760  # 10MB for large images
        )
        print(f"✓ Producer initialized, connected to Kafka at {kafka_bootstrap_servers}")
    
    def plot_waveform_with_probabilities(self, stream, annotations, picks, station_code):
        """Generate plot and return as base64 encoded string."""
        try:
            p_trace = annotations.select(channel="*_P")[0]
            s_trace = annotations.select(channel="*_S")[0]
            waveform = stream.select(channel="*Z")[0]
            
            waveform_times = waveform.times()
            prob_times = p_trace.times()
            
            fig, ax1 = plt.subplots(figsize=(15, 6))
            
            # Plot waveform
            ax1.plot(waveform_times, waveform.data, 'k-', linewidth=0.5, 
                    label='Waveform (Z)', alpha=0.7)
            ax1.set_xlabel('Time (seconds)', fontsize=12)
            ax1.set_ylabel('Amplitude', fontsize=12, color='k')
            ax1.tick_params(axis='y', labelcolor='k')
            ax1.grid(True, alpha=0.3)
            
            # Plot probabilities
            ax2 = ax1.twinx()
            ax2.plot(prob_times, p_trace.data, 'b-', linewidth=2, 
                    label='P-wave probability', alpha=0.8)
            ax2.plot(prob_times, s_trace.data, 'r-', linewidth=2, 
                    label='S-wave probability', alpha=0.8)
            ax2.set_ylabel('Probability', fontsize=12)
            ax2.set_ylim([0, 1])
            
            # Add pick markers
            if picks and len(picks.picks) > 0:
                starttime = waveform.stats.starttime
                for pick in picks.picks:
                    pick_time = pick.peak_time - starttime
                    color = 'blue' if pick.phase == 'P' else 'red'
                    ax1.axvline(pick_time, color=color, linestyle='--', 
                              linewidth=2, alpha=0.7)
                    ax1.text(pick_time, ax1.get_ylim()[1]*0.9, 
                           f'{pick.phase} ({pick.peak_value:.2f})', 
                           color=color, fontsize=10, ha='center')
            
            # Legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
            
            title = f"Station: {station_code} | {waveform.stats.starttime}"
            plt.title(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return image_base64
            
        except Exception as e:
            print(f"Error creating plot: {e}")
            return None
    
    def process_station(self, station_code, duration_minutes=5):
        """Process a single station and send results to Kafka."""
        print(f"\n{'='*60}")
        print(f"Processing station: {station_code}")
        print(f"{'='*60}")
        
        try:
            network, station = station_code.split(".")
            endtime = UTCDateTime()
            starttime = endtime - (60 * duration_minutes)
            
            # Fetch data
            print(f"Fetching data from IRIS...")
            stream = self.client.get_waveforms(
                network=network,
                station=station,
                location="*",
                channel="BH?",
                starttime=starttime,
                endtime=endtime
            )
            
            stream.merge(fill_value=0)
            stream.detrend('linear')
            print(f"✓ Data fetched: {len(stream)} traces")
            
            # Run PhaseNet
            print(f"Running PhaseNet analysis...")
            annotations = self.model.annotate(stream)
            picks = self.model.classify(stream)
            print(f"✓ Analysis complete: {len(picks.picks)} picks found")
            
            # Generate plot
            print(f"Generating visualization...")
            plot_base64 = self.plot_waveform_with_probabilities(
                stream, annotations, picks, station_code
            )
            
            # Prepare data for Kafka
            result_data = {
                'station_code': station_code,
                'timestamp': datetime.now().isoformat(),
                'start_time': str(starttime),
                'end_time': str(endtime),
                'num_picks': len(picks.picks),
                'picks': [],
                'plot_image': plot_base64,
                'stream_info': {
                    'num_traces': len(stream),
                    'sampling_rate': stream[0].stats.sampling_rate if len(stream) > 0 else 0
                }
            }
            
            # Add pick details
            for pick in picks.picks:
                result_data['picks'].append({
                    'phase': pick.phase,
                    'time': str(pick.peak_time),
                    'confidence': float(pick.peak_value),
                    'duration': float(pick.end_time - pick.start_time),
                    'trace_id': pick.trace_id
                })
            
            # Send to Kafka
            print(f"Sending results to Kafka topic 'seismic-data'...")
            future = self.producer.send('seismic-data', result_data)
            future.get(timeout=10)  # Wait for confirmation
            print(f"✓ Results sent to Kafka successfully!")
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing {station_code}: {e}")
            # Send error message to Kafka
            error_data = {
                'station_code': station_code,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }
            self.producer.send('seismic-data', error_data)
            return False
    
    def run_continuous(self, station_list, interval_seconds=300):
        """Continuously process stations in a loop."""
        print(f"Starting continuous monitoring...")
        print(f"Stations: {', '.join(station_list)}")
        print(f"Interval: {interval_seconds} seconds")
        
        while True:
            for station_code in station_list:
                self.process_station(station_code, duration_minutes=5)
                time.sleep(10)  # Small delay between stations
            
            print(f"\n⏰ Cycle complete. Waiting {interval_seconds} seconds before next cycle...")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    working_stations = [
        "GE.SUMG", "IU.AFI", "IU.ANMO", "IU.ANTO", "IU.BBSR",
        "IU.COLA", "IU.CTAO", "IU.FURI", "IU.GUMO", "IU.HRV",
        "IU.KONO", "IU.LSZ", "IU.MAJO", "IU.PAB", "IU.PMSA",
        "IU.POHA", "IU.RAR", "IU.SFJD", "IU.SSPA", "IU.TATO",
        "IU.TRIS", "IU.ULN", "IU.WCI", "IU.WVT", "BK.CMB"
    ]
    
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-service:9092')
    producer = SeismicDataProducer(kafka_bootstrap_servers=kafka_server)
    
    # Run continuously
    producer.run_continuous(working_stations, interval_seconds=600)
