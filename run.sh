#!/bin/bash
# run.sh - 启动 PulseAudio 和 FastAPI 应用

echo "=== 初始化音频服务 ==="

# 启动 PulseAudio
echo "启动 PulseAudio..."
pulseaudio --daemonize --system --disallow-exit --exit-idle-time=-1

# 检查 PulseAudio 是否启动成功
if pgrep -x "pulseaudio" > /dev/null; then
    echo "✓ PulseAudio 启动成功"
else
    echo "✗ PulseAudio 启动失败"
    exit 1
fi

# 等待 PulseAudio 完全启动
sleep 2

# 检查音频设备
echo "检查音频设备..."
pactl list sinks short

# 更新代码
cd /workdir/app
git pull

# 启动 FastAPI 应用
echo "启动 FastAPI 应用..."
uvicorn main:app --host 0.0.0.0 --port 6018