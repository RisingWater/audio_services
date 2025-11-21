# Audio Web Player

一个基于 Docker 的 Web 音频播放器，支持多音轨混音、流式播放和 RESTful API 控制。

## 🎯 功能特性

- 🎵 **多音轨混音** - 支持同时播放多个音频文件
- 🌐 **Web API** - 完整的 RESTful API 接口
- 📡 **流式播放** - 支持实时音频流播放
- 🔄 **会话管理** - 每个播放会话独立管理
- 🐳 **Docker 化** - 容器化部署，开箱即用
- 📊 **状态监控** - 实时查看播放状态和会话信息
- 🛠️ **TTS集成** - 集成edge-tts采用文字转语音直接播放

## 🚀 快速开始

### 前提条件

- Docker
- 音频输出设备

### 构建镜像

```bash
# 构建镜像
docker build -t audio-services .
```

### 运行容器
```bash
docker run -d \
    --name audio-services \
    --device /dev/snd:/dev/snd \
    -v ${WORKDIR}:/workdir \
    --group-add audio \
    -p 6018:6018 \
    --restart unless-stopped \
    audio-web-player
```

## 📖 API 文档

启动后访问：http://localhost:6018/docs

## 📄 许可证

MIT License
