#!/bin/bash

# 构建所有判题镜像

set -e

cd "$(dirname "$0")"

echo "🐳 开始构建判题镜像..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 构建 Python 镜像
echo -e "${BLUE}📦 构建 Python 判题镜像...${NC}"
docker build -f images/python.Dockerfile -t oj-judger-python:latest .
echo -e "${GREEN}✓ Python 镜像构建完成${NC}\n"

# 构建 C++ 镜像
echo -e "${BLUE}📦 构建 C++ 判题镜像...${NC}"
docker build -f images/cpp.Dockerfile -t oj-judger-cpp:latest .
echo -e "${GREEN}✓ C++ 镜像构建完成${NC}\n"

# 构建 Java 镜像
echo -e "${BLUE}📦 构建 Java 判题镜像...${NC}"
docker build -f images/java.Dockerfile -t oj-judger-java:latest .
echo -e "${GREEN}✓ Java 镜像构建完成${NC}\n"

# 构建 Go 镜像
echo -e "${BLUE}📦 构建 Go 判题镜像...${NC}"
docker build -f images/go.Dockerfile -t oj-judger-go:latest .
echo -e "${GREEN}✓ Go 镜像构建完成${NC}\n"

# 构建 JavaScript 镜像
echo -e "${BLUE}📦 构建 JavaScript 判题镜像...${NC}"
docker build -f images/javascript.Dockerfile -t oj-judger-javascript:latest .
echo -e "${GREEN}✓ JavaScript 镜像构建完成${NC}\n"

echo -e "${GREEN}🎉 所有镜像构建完成！${NC}"
echo ""
echo "📋 镜像列表："
docker images | grep oj-judger
