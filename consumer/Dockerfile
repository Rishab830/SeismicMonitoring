FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Flask app
COPY app.py .
COPY templates templates/

EXPOSE 5000

# Run Flask app
CMD ["python", "-u", "app.py"]
