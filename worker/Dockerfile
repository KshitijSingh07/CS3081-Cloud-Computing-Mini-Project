FROM python:3.11-slim
WORKDIR /app
COPY worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY worker/ /app/worker/
COPY prompts/ /app/prompts/
RUN mkdir -p /app/data /app/results
CMD ["python", "worker/label_worker.py"]
