FROM ubuntu:22.04

# 设置非交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装依赖 (包含 pulseaudio)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    ffmpeg \
    mplayer \
    sox \
    wget \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# 配置 PulseAudio
RUN mkdir -p /var/run/pulse && \
    chmod 755 /var/run/pulse && \
    echo "load-module module-native-protocol-unix auth-anonymous=1 socket=/var/run/pulse/native" > /etc/pulse/default.pa && \
    echo "load-module module-always-sink" >> /etc/pulse/default.pa && \
    echo "load-module module-suspend-on-idle" >> /etc/pulse/default.pa

# 安装 Python 依赖
RUN pip3 install fastapi uvicorn python-multipart aiofiles websockets

# 复制应用代码
COPY ./app /app/

WORKDIR /app

EXPOSE 6018

# 启动 PulseAudio 和应用
CMD pulseaudio --daemonize --system --disallow-exit --exit-idle-time=-1 && \
    uvicorn main:app --host 0.0.0.0 --port 6018