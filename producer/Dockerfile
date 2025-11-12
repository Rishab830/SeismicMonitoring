# Use even slimmer base
FROM python:3.10-slim-bullseye

# Install only minimal runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libopenblas0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && apt-get autoremove -y \
    && apt-get clean

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages with aggressive cleanup
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch torchvision --no-deps && \
    pip install --no-cache-dir -r requirements.txt && \
    # Remove pip cache
    rm -rf /root/.cache/pip

# Copy only the application code
COPY phasenet_producer.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run
CMD ["python", "-u", "phasenet_producer.py"]
