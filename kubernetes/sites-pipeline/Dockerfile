FROM python:3.6.8-alpine3.9
# show print output in logs (PYTHONUNBUFFERED)
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY cronjob.py ./
CMD ["python", "cronjob.py"]

