FROM python:3.6.8-alpine3.9
# show print output in logs (PYTHONUNBUFFERED)
ENV PYTHONUNBUFFERED=1
# You can override SUBSCRIBIE_IMAGE_NAME with
# kubernetes deployment config (see subscribie-k8s-cron-deployment.yaml)
ENV SUBSCRIBIE_IMAGE_NAME=subscribie/subscribie:latest
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY cronjob.py ./
CMD ["python", "cronjob.py"]

