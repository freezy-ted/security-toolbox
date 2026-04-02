FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    tcpdump \
    tshark \
    python3 \
    iproute2 \
    net-tools \
    && apt clean

RUN mkdir -p /output/network /toolbox/modules/network

COPY network.sh /toolbox/modules/network/network.sh
COPY network_report.py /toolbox/modules/network/network_report.py

RUN chmod +x /toolbox/modules/network/network.sh

WORKDIR /toolbox/modules/network

# Nécessite les droits réseau : docker run --privileged ou cap_add NET_RAW
# Usage : docker-compose run network eth0 300
ENTRYPOINT ["/toolbox/modules/network/network.sh"]
