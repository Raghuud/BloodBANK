FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PythonUNBUFFERED=1

# Set working directory in the container
WORKDIR /app

# Copy everything to /app in container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run"]
