FROM ubuntu:22.04

# 设置非交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 替换为阿里云源
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装依赖 (包含 pulseaudio)
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    vim \
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
    locales \
    locales-all

# 添加用户
RUN useradd -m -u 1000 appuser && \
    usermod -a -G audio,pulse,pulse-access sudo appuser

# 配置 PulseAudio
RUN mkdir -p /var/run/pulse && \
    chown appuser:appuser /var/run/pulse && \
    chmod 755 /var/run/pulse && \
    echo "load-module module-native-protocol-unix auth-anonymous=1 socket=/var/run/pulse/native" > /etc/pulse/default.pa && \
    echo "load-module module-always-sink" >> /etc/pulse/default.pa && \
    echo "load-module module-suspend-on-idle" >> /etc/pulse/default.pa

# 从 GitHub 克隆代码
RUN pip3 install fastapi uvicorn python-multipart aiofiles websockets edge-tts playsound load_dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple/

git config --global --add safe.directory "*"

COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]