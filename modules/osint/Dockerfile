FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    whois \
    dnsutils \
    theharvester \
    recon-ng \
    python3 \
    python3-pip \
    curl \
    unzip \
    git \
    amass \
    && apt clean

# Subfinder
RUN curl -sL https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip \
    -o /tmp/subfinder.zip && \
    unzip /tmp/subfinder.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/subfinder && \
    rm /tmp/subfinder.zip

# Shodan CLI
RUN pip3 install shodan --break-system-packages

RUN mkdir -p /output/osint /toolbox/modules/osint

COPY osint.sh             /toolbox/modules/osint/osint.sh
COPY osint_report.py      /toolbox/modules/osint/osint_report.py
COPY recon_ng_commands.rc /toolbox/modules/osint/recon_ng_commands.rc

RUN chmod +x /toolbox/modules/osint/osint.sh

WORKDIR /toolbox/modules/osint

# Variables optionnelles :
# -e SHODAN_API_KEY=votre_clé
# Usage : docker-compose run osint example.com domain
ENTRYPOINT ["/toolbox/modules/osint/osint.sh"]
