FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (including src folder)
COPY . .

# Create a non-root user for security
RUN useradd -m -r botuser && \
    chown -R botuser:botuser /app
USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose the port Cloud Run expects
EXPOSE $PORT

# Run the application from the src directory
WORKDIR /app/src
CMD ["python", "main.py"]