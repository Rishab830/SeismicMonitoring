from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# In-memory storage for latest seismic data
seismic_data_store = {}
data_lock = threading.Lock()

# Station list
STATIONS = {
    "GE.SUMG": "Summit Camp, Greenland",
    "IU.AFI": "Afiamalu, Samoa",
    "IU.ANMO": "Albuquerque, New Mexico, USA",
    "IU.ANTO": "Ankara, Turkey",
    "IU.BBSR": "St. George's, Bermuda",
    "IU.COLA": "College Outpost, Alaska, USA",
    "IU.CTAO": "Charters Towers, Australia",
    "IU.FURI": "Mt. Furi, Ethiopia",
    "IU.GUMO": "Guam, Mariana Islands",
    "IU.HRV": "Adam Dziewonski Observatory, Massachusetts, USA",
    "IU.KONO": "Kongsberg, Norway",
    "IU.LSZ": "Lusaka, Zambia",
    "IU.MAJO": "Matsushiro, Japan",
    "IU.PAB": "San Pablo, Spain",
    "IU.PMSA": "Palmer Station, Antarctica",
    "IU.POHA": "Pohakuloa, Hawaii, USA",
    "IU.RAR": "Rarotonga, Cook Islands",
    "IU.SFJD": "Sondre Stromfjord, Greenland",
    "IU.SSPA": "Standing Stone, Pennsylvania, USA",
    "IU.TATO": "Taipei, Taiwan",
    "IU.TRIS": "Tristan da Cunha",
    "IU.ULN": "Ulaanbaatar, Mongolia",
    "IU.WCI": "Wyandotte Cave, Indiana, USA",
    "IU.WVT": "Waverly, Tennessee, USA",
    "BK.CMB": "Columbia College, California, USA"
}

def kafka_consumer_thread():
    """Background thread to consume Kafka messages."""
    kafka_server = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-service:9092')
    consumer = KafkaConsumer(
        'seismic-data',
        bootstrap_servers=kafka_server,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='seismic-consumer-group'
    )
    
    print(f"✓ Consumer connected to Kafka at {kafka_server}")
    print("Waiting for messages...")
    
    for message in consumer:
        data = message.value
        station_code = data.get('station_code')
        
        if station_code:
            with data_lock:
                seismic_data_store[station_code] = data
            print(f"✓ Received data for {station_code} - {len(data.get('picks', []))} picks")

# Start Kafka consumer in background thread
consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
consumer_thread.start()

@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')

@app.route('/api/stations')
def get_stations():
    """Get list of all available stations."""
    return jsonify({
        'stations': [
            {'code': code, 'name': name} 
            for code, name in STATIONS.items()
        ]
    })

@app.route('/api/seismic-data/<station_code>')
def get_seismic_data(station_code):
    """Get the latest seismic data for a specific station."""
    with data_lock:
        print(seismic_data_store.keys())
        data = seismic_data_store.get(station_code)

    if data:
        return jsonify({
            'success': True,
            'data': data
        })
    else:
        return jsonify({
            'success': False,
            'message': f'No data available for station {station_code} yet. Please wait for the next processing cycle.'
        }), 404

@app.route('/api/all-data')
def get_all_data():
    """Get all available seismic data."""
    with data_lock:
        all_data = dict(seismic_data_store)
    
    return jsonify({
        'success': True,
        'count': len(all_data),
        'data': all_data
    })

@app.route('/api/health')
def health():
    """Health check endpoint."""
    with data_lock:
        data_count = len(seismic_data_store)
    
    return jsonify({
        'status': 'healthy',
        'stations_with_data': data_count,
        'total_stations': len(STATIONS)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
