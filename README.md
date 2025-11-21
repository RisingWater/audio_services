# Audio Web Player

一个基于 Docker 的 Web 音频播放器，支持多音轨混音、流式播放和 RESTful API 控制。

## 🎯 功能特性

- 🎵 **多音轨混音** - 支持同时播放多个音频文件
- 🌐 **Web API** - 完整的 RESTful API 接口
- 📡 **流式播放** - 支持实时音频流播放
- 🔄 **会话管理** - 每个播放会话独立管理
- 🐳 **Docker 化** - 容器化部署，开箱即用
- 📊 **状态监控** - 实时查看播放状态和会话信息

## 🚀 快速开始

### 前提条件

- Docker
- 音频输出设备

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd audio-web-player

# 使用 Docker Compose 启动
./docker-compose-run.sh
```

或者手动启动：

```bash
# 构建镜像
docker build -t audio-web-player .

# 运行容器
docker run -d \
    --name audio-web-player \
    --device /dev/snd:/dev/snd \
    --group-add audio \
    -p 8000:8000 \
    --restart unless-stopped \
    audio-web-player
```

## 📖 API 文档

启动后访问：http://localhost:8000/docs

### 主要接口

#### 播放音频文件
```bash
POST /api/play
Content-Type: multipart/form-data

curl -X POST -F "file=@audio.mp3" -F "volume=0.8" http://localhost:8000/api/play
```

#### 流式播放
```bash
# 创建流式会话
POST /api/stream/start?volume=0.8

# 发送音频数据
POST /api/stream/{session_id}/feed
Content-Type: multipart/form-data

# 直接流式播放
POST /api/stream/direct
Content-Type: multipart/form-data
```

#### 管理会话
```bash
# 获取所有会话
GET /api/sessions

# 获取特定会话状态
GET /api/sessions/{session_id}

# 停止会话
POST /api/sessions/{session_id}/stop

# 调整音量
POST /api/sessions/{session_id}/volume
Content-Type: application/json
{"volume": 0.5}

# 停止所有会话
POST /api/stop-all
```

#### WebSocket 流式接口
```bash
# WebSocket 连接
ws://localhost:8000/api/ws/stream/{session_id}
```

## 🛠️ 管理命令

使用管理脚本方便地操作容器：

```bash
# 查看使用帮助
./audio-player-manager.sh

# 启动服务
./audio-player-manager.sh start

# 停止服务
./audio-player-manager.sh stop

# 查看状态
./audio-player-manager.sh status

# 查看日志
./audio-player-manager.sh logs

# 重新构建
./audio-player-manager.sh build

# 测试播放
./audio-player-manager.sh test
```

## 🎮 使用示例

### 1. 播放本地音频文件
```bash
curl -X POST -F "file=@music.mp3" http://localhost:8000/api/play
```

### 2. 同时播放多个音轨
```bash
# 第一个音轨
curl -X POST -F "file=@vocals.wav" -F "volume=0.8" http://localhost:8000/api/play

# 第二个音轨（同时播放）
curl -X POST -F "file=@background.mp3" -F "volume=0.5" http://localhost:8000/api/play
```

### 3. 流式播放示例
```bash
# 创建流式会话
SESSION=$(curl -s -X POST "http://localhost:8000/api/stream/start" | jq -r '.session_id')

# 发送音频数据块
curl -X POST -F "file=@chunk1.wav" "http://localhost:8000/api/stream/$SESSION/feed"
curl -X POST -F "file=@chunk2.wav" "http://localhost:8000/api/stream/$SESSION/feed"
```

### 4. 查看播放状态
```bash
# 查看所有会话
curl http://localhost:8000/api/sessions | jq .

# 查看特定会话
curl http://localhost:8000/api/sessions/$SESSION_ID | jq .
```

## 📁 项目结构

```
audio-web-player/
├── main.py                 # FastAPI 主应用
├── config.py               # 配置管理
├── models/                 # 数据模型
│   ├── session.py          # 会话模型
│   └── response.py         # 响应模型
├── managers/               # 管理器类
│   └── audio_manager.py    # 音频管理器
├── routes/                 # API 路由
│   ├── sessions.py         # 会话路由
│   ├── streams.py          # 流式路由
│   └── websocket.py        # WebSocket 路由
├── utils/                  # 工具函数
│   ├── audio_utils.py      # 音频工具
│   └── file_utils.py       # 文件工具
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile              # Docker 构建文件
└── scripts/                # 管理脚本
    ├── docker-compose-run.sh
    ├── audio-player-manager.sh
    └── test-audio-api.sh
```

## ⚙️ 配置说明

### 音频配置
- 采样率：44100 Hz
- 声道数：立体声 (2 channels)
- 支持格式：WAV, MP3, OGG, FLAC
- 混音引擎：PulseAudio

### 会话配置
- 会话清理间隔：5分钟
- 会话过期时间：10分钟
- 最大并发会话：无限制

## 🔧 故障排除

### 常见问题

1. **没有音频输出**
   - 检查音频设备权限
   - 确认 `/dev/snd` 设备已挂载
   - 查看容器日志：`docker logs audio-web-player`

2. **权限错误**
   - 确保用户有音频设备访问权限
   - 尝试使用 `--privileged` 模式运行

3. **端口冲突**
   - 修改 `docker-compose.yml` 中的端口映射
   - 使用 `-p 8080:8000` 指定其他端口

### 查看日志
```bash
docker-compose logs -f
# 或
docker logs -f audio-web-player
```

## 📝 开发说明

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 添加新功能
1. 在 `models/` 中添加数据模型
2. 在 `routes/` 中添加 API 路由
3. 在 `utils/` 中添加业务逻辑
4. 更新 API 文档

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请提交 [Issue](https://github.com/your-repo/audio-web-player/issues) 或联系维护者。

---

**享受你的音频播放体验！** 🎧