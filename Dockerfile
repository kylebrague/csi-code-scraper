FROM alpine:latest
RUN apk add --no-cache \
    udev \
    ttf-freefont \
    xvfb \
    xorg-server \
    dbus \
    curl \
    unzip
RUN curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/
RUN apk add python3
RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install selenium==4.25.0
RUN cp -r /opt/chrome-linux64 /opt/chrome
RUN cp /opt/chromedriver-linux64/chromedriver /opt/chromedriver
COPY main.py /opt/
WORKDIR /opt/
CMD ["./venv/bin/python", "main.py"]

