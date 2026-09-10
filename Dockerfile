# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root system user for security
RUN groupadd -r pydah && useradd -r -g pydah pydahuser

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Initialize/seed SQLite database
RUN python init_db.py

# Grant ownership to non-root user
RUN chown -R pydahuser:pydah /app

# Switch to non-root user
USER pydahuser

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Expose default port
EXPOSE 5000

# Health check to ensure service is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request, os; urllib.request.urlopen('http://localhost:' + str(os.environ.get('PORT', 5000)))" || exit 1

# Production WSGI command with dynamic port and concurrency
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 60 app:app"]
