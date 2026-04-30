FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    whois \
    dnsutils \
    theharvester \
    recon-ng \
    python3 \
    python3-pip \
    git \
    amass \
    subfinder \
    && apt clean

RUN pip3 install shodan --break-system-packages

RUN mkdir -p /output/osint /toolbox/modules/osint

COPY osint.sh /toolbox/modules/osint/osint.sh
COPY osint_report.py /toolbox/modules/osint/osint_report.py
COPY recon_ng_commands.rc /toolbox/modules/osint/recon_ng_commands.rc

RUN chmod +x /toolbox/modules/osint/osint.sh

WORKDIR /toolbox/modules/osint

ENTRYPOINT ["/toolbox/modules/osint/osint.sh"]
