#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始构建音频播放器 Docker 镜像...${NC}"

# 构建 Docker 镜像
docker build -t audio-web-player .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker 镜像构建失败！${NC}"
    exit 1
fi

echo -e "${GREEN}Docker 镜像构建成功！${NC}"