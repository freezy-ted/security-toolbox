FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    nmap \
    whois \
    dnsrecon \
    theharvester \
    subfinder \
    python3 \
    python3-pip \
    curl \
    git \
    && apt clean

RUN pip3 install shodan --break-system-packages

RUN mkdir -p /output/recon /toolbox/modules/recon

COPY recon.sh /toolbox/modules/recon/recon.sh
COPY recon_report.py /toolbox/modules/recon/recon_report.py

RUN chmod +x /toolbox/modules/recon/recon.sh

WORKDIR /toolbox/modules/recon

# Configuration theHarvester avec clé Shodan
RUN sed -i 's/shodan:/shodan:\n  key: ${SHODAN_API_KEY}/' /etc/theHarvester/api-keys.yaml

ENTRYPOINT ["/toolbox/modules/recon/recon.sh"]
