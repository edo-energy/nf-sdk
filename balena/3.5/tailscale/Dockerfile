FROM tailscale/tailscale:latest

ADD ZscalerRootCertificate-2048-SHA256.crt /usr/local/share/ca-certificates/ZscalerRootCertificate-2048-SHA256.crt

USER root

RUN apk update && apk upgrade --available && update-ca-certificates
