FROM python:3.11-slim

RUN pip install flask --break-system-packages 2>/dev/null || pip install flask

RUN apt update && apt install -y docker.io && apt clean

RUN mkdir -p /output /toolbox/modules /app/templates

COPY app.py /app/app.py
COPY templates/ /app/templates/

WORKDIR /app
EXPOSE 5000

CMD ["python3", "app.py"]
