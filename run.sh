#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 停止并删除现有容器（如果存在）
echo -e "${YELLOW}停止现有容器...${NC}"
docker stop audio-web-player 2>/dev/null || true
docker rm audio-web-player 2>/dev/null || true

# 运行容器
echo -e "${GREEN}启动音频播放器容器...${NC}"
docker run -d \
    --name audio-web-player \
    --device /dev/snd:/dev/snd \
    --group-add audio \
    -p 6018:6018 \
    --restart unless-stopped \
    audio-web-player

echo -e "${GREEN}音频播放器已启动！${NC}"
echo -e "${YELLOW}访问地址: http://localhost:6018${NC}"
echo -e "${YELLOW}API 文档: http://localhost:6018/docs${NC}"