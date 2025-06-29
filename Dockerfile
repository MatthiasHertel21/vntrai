FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir python-dotenv

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Expose port 5004
EXPOSE 5004

# Command to run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5004"]
