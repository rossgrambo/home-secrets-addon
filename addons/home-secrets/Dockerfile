ARG BUILD_FROM=ghcr.io/hassio-addons/base:17.1.0
FROM ${BUILD_FROM}

# Add Python & git
RUN apk add --no-cache python3 py3-pip git

# Copy app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# S6 overlay expects /run.sh as entrypoint script via "init: false"
CMD [ "/app/run.sh" ]