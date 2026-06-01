FROM normalframework.azurecr.io/normalframework/nf-full:3.10.4-3

# libfaketime for time acceleration (optional, non-fatal if unavailable)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libfaketime && \
    rm -rf /var/lib/apt/lists/* || true

# Create faketime directory (offset file written by time-controller)
RUN mkdir -p /faketime && echo "+0" > /faketime/offset
