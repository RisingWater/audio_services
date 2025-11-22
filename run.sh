#!/bin/bash
# run.sh - 启动 PulseAudio 和 FastAPI 应用

echo "=== 初始化音频服务 ==="

# 启动 PulseAudio
echo "启动 PulseAudio..."
pulseaudio --start --exit-idle-time=-1 --log-target=stderr &

# 等待 PulseAudio 启动
sleep 3

# 检查 PulseAudio 是否可用
if pactl info &> /dev/null; then
    echo "✓ PulseAudio 启动成功"
    
    # 检查音频设备
    echo "检查音频设备..."
    pactl list sinks short
else
    echo "✗ PulseAudio 启动失败，将继续使用 ALSA"
fi

# 切换到工作目录
cd /workdir/app

# 更新代码（如果有权限）
if [ -d .git ] && git status &> /dev/null; then
    echo "更新代码..."
    git pull
else
    echo "跳过代码更新"
fi

# 启动 FastAPI 应用
echo "启动 FastAPI 应用..."
uvicorn main:app --host 0.0.0.0 --port 6018