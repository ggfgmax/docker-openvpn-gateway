# Original credit: https://github.com/jpetazzo/dockvpn

# Smallest base image
FROM docker.m.daocloud.io/alpine:3.23.2

MAINTAINER Kyle Manna <kyle@kylemanna.com>

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk add --update openvpn iptables bash easy-rsa openvpn-auth-pam google-authenticator pamtester \
    iproute2 curl libldap openldap-clients pam-ldap python3 py3-pip && \
    ln -s /usr/share/easy-rsa/easyrsa /usr/local/bin && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

# Needed by scripts
ENV OPENVPN /etc/openvpn
ENV EASYRSA /usr/share/easy-rsa
ENV EASYRSA_PKI $OPENVPN/pki
ENV EASYRSA_VARS_FILE $OPENVPN/vars

# Gateway mode control (0=normal VPN, 1=gateway mode)
ENV GATEWAY_MODE 0

# LDAP authentication control (0=disabled, 1=enabled)
ENV LDAP_ENABLED 0

VOLUME ["/etc/openvpn"]

# Internally uses port 1194/udp, remap using `docker run -p 443:1194/tcp`
EXPOSE 1194/udp

WORKDIR /etc/openvpn


ADD ./bin /usr/local/bin
RUN chmod a+x /usr/local/bin/*

# Add support for OTP authentication using a PAM module
ADD ./otp/openvpn /etc/pam.d/

# Create directories for multi-cloud gateway functionality
RUN mkdir -p /etc/openvpn/sites /etc/openvpn/site-pids /var/log

# Add scripts
ADD ./scripts /usr/share/doc/openvpn/scripts
RUN chmod +x /usr/share/doc/openvpn/scripts/*.sh 2>/dev/null || true && \
    chmod +x /usr/share/doc/openvpn/scripts/setup/*.sh 2>/dev/null || true && \
    chmod +x /usr/share/doc/openvpn/scripts/tests/*.sh 2>/dev/null || true

# Add documentation
ADD ./docs /usr/share/doc/openvpn/docs

# Add Web UI
ADD ./webui /opt/openvpn-webui
RUN pip3 install --no-cache-dir -r /opt/openvpn-webui/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    chmod +x /opt/openvpn-webui/app.py

# Expose Web UI port
EXPOSE 8080
CMD ["bash","-c","ovpn_run & ovpn_run_webui"]