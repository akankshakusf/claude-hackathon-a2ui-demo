FROM python:3.12-slim
WORKDIR /app

# Install minimal build deps
RUN apt-get update && apt-get install -y curl gcc && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . .

# Install dependencies directly — bypasses pyproject.toml
RUN pip install --no-cache-dir a2a-sdk anthropic jsonschema python-dotenv uvicorn starlette click

# Expose port (Railway injects PORT)
EXPOSE 10002

# Start server (PORT env var handled via Click's envvar parameter)
CMD ["python", "-m", "agent"]