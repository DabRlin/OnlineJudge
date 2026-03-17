#!/bin/bash

# 启动判题服务脚本

set -e

echo "🚀 启动 Online Judge 判题服务"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 启动 Redis
echo -e "${BLUE}📦 启动 Redis...${NC}"
docker-compose -f docker-compose.judger.yml up -d
echo -e "${GREEN}✓ Redis 已启动${NC}"
echo ""

# 2. 等待 Redis 就绪
echo -e "${BLUE}⏳ 等待 Redis 就绪...${NC}"
sleep 2
echo -e "${GREEN}✓ Redis 就绪${NC}"
echo ""

# 3. 提示启动 Celery Worker
echo -e "${YELLOW}📝 请在新终端中启动 Celery Worker:${NC}"
echo ""
echo "  cd src/backend"
echo "  source .venv/bin/activate"
echo "  export PYTHONPATH=\$(pwd)/.."
echo "  celery -A judger.celery_app worker --loglevel=info --concurrency=2"
echo ""

# 4. 提示启动后端
echo -e "${YELLOW}📝 请在另一个终端中启动后端:${NC}"
echo ""
echo "  cd src/backend"
echo "  source .venv/bin/activate"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""

# 5. 查看服务状态
echo -e "${BLUE}📊 服务状态:${NC}"
docker-compose -f docker-compose.judger.yml ps
echo ""

echo -e "${GREEN}✅ 判题服务准备就绪！${NC}"
