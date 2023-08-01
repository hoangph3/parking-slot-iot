# FROM ubuntu:18.04
FROM hoangph3/parking-slot:1.0.0

WORKDIR /app

COPY . .

ENV DEBIAN_FRONTEND=noninteractive

# Add user
# RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

# Install Python 3, PyQt5
RUN apt-get update && apt-get install -y python3-pyqt5 python3-pip nano telnet curl && \
    pip3 install -U pip && pip3 install -r requirements.txt

CMD [ "python3", "main.py" ]
