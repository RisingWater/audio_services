#!/bin/bash

# 切换到工作目录
cd /workdir

# 更新代码（如果有权限）
if [ -d .git ] && git status &> /dev/null; then
    echo "更新代码..."
    git pull
else
    echo "跳过代码更新"
fi

# 启动 PulseAudio
echo "启动 PulseAudio..."

# 先杀死可能存在的 PulseAudio 进程
pulseaudio --kill 2>/dev/null || true
sleep 2

# 启动 PulseAudio
pulseaudio --start --exit-idle-time=-1 --log-target=stderr &

# 等待并检查 PulseAudio 是否可用
MAX_RETRIES=30
RETRY_COUNT=0
PULSE_STARTED=false

echo "等待 PulseAudio 启动..."

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if pactl info &> /dev/null; then
        PULSE_STARTED=true
        echo "✓ PulseAudio 启动成功"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "等待 PulseAudio 启动... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ "$PULSE_STARTED" = false ]; then
    echo "✗ PulseAudio 启动失败，尝试强制重启..."
    
    # 强制杀死所有相关进程
    killall pulseaudio 2>/dev/null || true
    sleep 3
    
    # 再次尝试启动
    pulseaudio --start --exit-idle-time=-1 --log-target=stderr &
    sleep 5
    
    if pactl info &> /dev/null; then
        echo "✓ PulseAudio 强制启动成功"
        PULSE_STARTED=true
    else
        echo "✗ PulseAudio 启动彻底失败，将退出"
        exit 1
    fi
fi

# 只有 PulseAudio 启动成功后才执行后续操作
if [ "$PULSE_STARTED" = true ]; then
    # 卸载 null sink（如果存在）
    echo "清理现有音频模块..."
    pactl unload-module module-null-sink 2>/dev/null || true
    pactl unload-module module-alsa-sink 2>/dev/null || true
    sleep 1

    # 加载真实的 ALSA 设备
    echo "加载真实音频设备到 PulseAudio..."
    ALSA_MODULE=$(pactl load-module module-alsa-sink device=hw:0,0 sink_name=alsa_output 2>/dev/null)
    
    if [ -n "$ALSA_MODULE" ]; then
        echo "✓ ALSA 设备加载成功，模块ID: $ALSA_MODULE"
        
        # 设置默认设备
        pactl set-default-sink alsa_output
        
        # 设置音量
        pactl set-sink-volume alsa_output 80%
        
        # 检查音频设备
        echo "当前音频设备状态:"
        pactl list sinks short
        
        echo "✓ 音频系统初始化完成"
    else
        echo "✗ ALSA 设备加载失败"
        exit 1
    fi
fi


cd /workdir/app

# 启动 FastAPI 应用
echo "启动 FastAPI 应用..."
uvicorn main:app --host 0.0.0.0 --port 6018