FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    nikto \
    gobuster \
    ffuf \
    python3 \
    wordlists \
    dirb \
    && apt clean

RUN mkdir -p /output/web /toolbox/modules/web_audit

COPY web_audit.sh /toolbox/modules/web_audit/web_audit.sh
COPY web_report.py /toolbox/modules/web_audit/web_report.py

RUN chmod +x /toolbox/modules/web_audit/web_audit.sh

WORKDIR /toolbox/modules/web_audit

# Usage : docker-compose run web_audit http://example.com
ENTRYPOINT ["/toolbox/modules/web_audit/web_audit.sh"]
