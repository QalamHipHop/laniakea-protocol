# Stage 1: Build the frontend (if needed, assuming a simple static build for now)
# Since the web directory contains static HTML/JS/CSS, we'll serve it with the backend.
# If a build step was required (e.g., React/Vue), it would go here.

# Stage 2: Build the backend (FastAPI)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . $APP_HOME

# Expose the port the FastAPI app will run on
EXPOSE 8000

# Command to run the application
# Assuming the main FastAPI app is in laniakea/network/api.py and the app instance is named 'app'
CMD ["uvicorn", "laniakea.network.api:app", "--host", "0.0.0.0", "--port", "8000"]
