FROM python:3.11-slim

RUN pip install weasyprint jinja2 --break-system-packages 2>/dev/null || \
    pip install weasyprint jinja2

RUN mkdir -p /output /toolbox/modules/reporting

COPY generate.py /toolbox/modules/reporting/generate.py

WORKDIR /toolbox/modules/reporting

# Usage : docker-compose run reporting --target example.com --output /output/report_final.html
ENTRYPOINT ["python3", "/toolbox/modules/reporting/generate.py"]
