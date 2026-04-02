FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    nmap \
    whois \
    dnsrecon \
    theharvester \
    python3 \
    python3-pip \
    curl \
    git \
    && apt clean

# Subfinder (Go binary)
RUN curl -sL https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip \
    -o /tmp/subfinder.zip && \
    unzip /tmp/subfinder.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/subfinder && \
    rm /tmp/subfinder.zip

# Shodan CLI (optionnel)
RUN pip3 install shodan --break-system-packages

RUN mkdir -p /output/recon /toolbox/modules/recon

COPY recon.sh /toolbox/modules/recon/recon.sh
COPY recon_report.py /toolbox/modules/recon/recon_report.py

RUN chmod +x /toolbox/modules/recon/recon.sh

# Lien symbolique pour que /output soit accessible facilement
RUN ln -sf /output /output

WORKDIR /toolbox/modules/recon

# Usage : docker run --rm -v $(pwd)/output:/output recon example.com
ENTRYPOINT ["/toolbox/modules/recon/recon.sh"]
