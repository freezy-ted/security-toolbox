FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    nmap \
    python3 \
    git \
    nuclei \
    && apt clean

RUN nuclei -update-templates -silent 2>/dev/null || true

RUN mkdir -p /output/vuln /toolbox/modules/vuln

COPY vuln.sh /toolbox/modules/vuln/vuln.sh
COPY vuln_report.py /toolbox/modules/vuln/vuln_report.py

RUN chmod +x /toolbox/modules/vuln/vuln.sh

WORKDIR /toolbox/modules/vuln

ENTRYPOINT ["/toolbox/modules/vuln/vuln.sh"]
