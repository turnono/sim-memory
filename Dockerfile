FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# CRITICAL: Install the problematic dependencies first, explicitly
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir deprecated==1.2.14
RUN pip install --no-cache-dir wrapt>=1.14.0
RUN pip install --no-cache-dir opentelemetry-semantic-conventions>=1.20.0
RUN pip install --no-cache-dir opentelemetry-api>=1.20.0
RUN pip install --no-cache-dir opentelemetry-sdk>=1.20.0

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Create user and set permissions
RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

# Copy application code
COPY . .

# Set user
USER myuser

# Set environment variables
ENV PATH="/home/myuser/.local/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application using uvicorn with main:app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]