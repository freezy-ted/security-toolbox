FROM kalilinux/kali-rolling

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-impacket \
    ldap-utils \
    enum4linux \
    git \
    && apt clean

# ldapdomaindump
RUN pip3 install ldapdomaindump --break-system-packages

# bloodhound-python
RUN pip3 install bloodhound --break-system-packages

# enum4linux-ng
RUN git clone --depth 1 https://github.com/cddmp/enum4linux-ng.git /opt/enum4linux-ng && \
    pip3 install -r /opt/enum4linux-ng/requirements.txt --break-system-packages && \
    ln -s /opt/enum4linux-ng/enum4linux-ng.py /usr/local/bin/enum4linux-ng && \
    chmod +x /opt/enum4linux-ng/enum4linux-ng.py

RUN mkdir -p /output/ad /toolbox/modules/ad_audit

COPY ad_audit.sh /toolbox/modules/ad_audit/ad_audit.sh
COPY ad_report.py /toolbox/modules/ad_audit/ad_report.py

RUN chmod +x /toolbox/modules/ad_audit/ad_audit.sh

WORKDIR /toolbox/modules/ad_audit

# Usage : docker-compose run ad_audit <DC_IP> <domaine> <user> <password>
ENTRYPOINT ["/toolbox/modules/ad_audit/ad_audit.sh"]
