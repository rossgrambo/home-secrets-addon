# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM=ghcr.io/hassio-addons/base:17.1.0
FROM $BUILD_FROM

# Add Python & git
RUN apk add --no-cache python3 py3-pip git

# Install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Copy service configuration
COPY rootfs/etc /etc

# Copy application code
COPY app /app

# Make service scripts executable
RUN chmod +x /etc/services.d/home-secrets/run /etc/services.d/home-secrets/finish