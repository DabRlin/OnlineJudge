.PHONY: help setup dev build test clean install-tools backend-dev frontend-dev

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## 显示帮助信息
	@echo "$(BLUE)Online Judge 系统 - 可用命令:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

install-tools: ## 安装开发工具（uv 和 bun）
	@echo "$(BLUE)安装 uv...$(RESET)"
	@curl -LsSf https://astral.sh/uv/install.sh | sh || echo "$(YELLOW)uv 可能已安装$(RESET)"
	@echo "$(BLUE)安装 bun...$(RESET)"
	@curl -fsSL https://bun.sh/install | bash || echo "$(YELLOW)bun 可能已安装$(RESET)"
	@echo "$(GREEN)✓ 工具安装完成$(RESET)"

setup: install-tools ## 初始化开发环境（安装所有依赖）
	@echo "$(BLUE)初始化后端环境...$(RESET)"
	@cd backend && uv venv && uv pip install -r requirements.txt -r requirements-dev.txt
	@echo "$(GREEN)✓ 后端依赖安装完成$(RESET)"
	@echo ""
	@echo "$(BLUE)初始化前端环境...$(RESET)"
	@cd frontend && bun install
	@echo "$(GREEN)✓ 前端依赖安装完成$(RESET)"
	@echo ""
	@echo "$(BLUE)复制环境变量文件...$(RESET)"
	@[ ! -f backend/.env ] && cp backend/.env.example backend/.env || echo "backend/.env 已存在"
	@[ ! -f frontend/.env ] && cp frontend/.env.example frontend/.env || echo "frontend/.env 已存在"
	@echo "$(GREEN)✓ 环境变量文件已创建$(RESET)"
	@echo ""
	@echo "$(GREEN)✓ 开发环境初始化完成！$(RESET)"
	@echo "$(YELLOW)提示: 请编辑 backend/.env 和 frontend/.env 配置环境变量$(RESET)"

redis: ## 启动 Redis（Docker）
	@echo "$(BLUE)启动 Redis...$(RESET)"
	@docker-compose up -d redis
	@echo "$(GREEN)✓ Redis 已启动$(RESET)"

postgres: ## 启动 PostgreSQL（Docker）
	@echo "$(BLUE)启动 PostgreSQL...$(RESET)"
	@docker-compose --profile full up -d postgres
	@echo "$(GREEN)✓ PostgreSQL 已启动$(RESET)"

db-migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(RESET)"
	@cd backend && alembic upgrade head
	@echo "$(GREEN)✓ 数据库迁移完成$(RESET)"

db-reset: ## 重置数据库（危险操作！）
	@echo "$(RED)警告: 这将删除所有数据！$(RESET)"
	@read -p "确认继续? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -f backend/oj.db
	@cd backend && alembic upgrade head
	@echo "$(GREEN)✓ 数据库已重置$(RESET)"

backend-dev: ## 启动后端开发服务器
	@echo "$(BLUE)启动后端开发服务器...$(RESET)"
	@cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## 启动前端开发服务器
	@echo "$(BLUE)启动前端开发服务器...$(RESET)"
	@cd frontend && bun run dev

dev: redis ## 启动完整开发环境（Redis + 后端 + 前端）
	@echo "$(GREEN)启动开发环境...$(RESET)"
	@echo "$(YELLOW)提示: 在不同终端窗口运行以下命令:$(RESET)"
	@echo "  1. $(BLUE)make backend-dev$(RESET)  - 启动后端"
	@echo "  2. $(BLUE)make frontend-dev$(RESET) - 启动前端"
	@echo ""
	@echo "或使用 tmux/screen 同时运行"

test: ## 运行所有测试
	@echo "$(BLUE)运行后端测试...$(RESET)"
	@cd backend && pytest
	@echo "$(BLUE)运行前端测试...$(RESET)"
	@cd frontend && bun test
	@echo "$(GREEN)✓ 所有测试完成$(RESET)"

test-backend: ## 运行后端测试
	@echo "$(BLUE)运行后端测试...$(RESET)"
	@cd backend && pytest -v
	@echo "$(GREEN)✓ 后端测试完成$(RESET)"

test-frontend: ## 运行前端测试
	@echo "$(BLUE)运行前端测试...$(RESET)"
	@cd frontend && bun test
	@echo "$(GREEN)✓ 前端测试完成$(RESET)"

coverage: ## 生成测试覆盖率报告
	@echo "$(BLUE)生成后端测试覆盖率...$(RESET)"
	@cd backend && pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ 覆盖率报告已生成: backend/htmlcov/index.html$(RESET)"

lint: ## 代码检查
	@echo "$(BLUE)检查后端代码...$(RESET)"
	@cd backend && ruff check . && black --check .
	@echo "$(BLUE)检查前端代码...$(RESET)"
	@cd frontend && bun run lint
	@echo "$(GREEN)✓ 代码检查完成$(RESET)"

format: ## 格式化代码
	@echo "$(BLUE)格式化后端代码...$(RESET)"
	@cd backend && ruff check --fix . && black .
	@echo "$(BLUE)格式化前端代码...$(RESET)"
	@cd frontend && bun run format
	@echo "$(GREEN)✓ 代码格式化完成$(RESET)"

build: ## 构建生产版本
	@echo "$(BLUE)构建前端...$(RESET)"
	@cd frontend && bun run build
	@echo "$(GREEN)✓ 构建完成$(RESET)"

docker-build: ## 构建 Docker 镜像
	@echo "$(BLUE)构建 Docker 镜像...$(RESET)"
	@docker-compose build
	@echo "$(GREEN)✓ Docker 镜像构建完成$(RESET)"

docker-up: ## 启动所有 Docker 服务
	@echo "$(BLUE)启动所有服务...$(RESET)"
	@docker-compose up -d
	@echo "$(GREEN)✓ 所有服务已启动$(RESET)"

docker-down: ## 停止所有 Docker 服务
	@echo "$(BLUE)停止所有服务...$(RESET)"
	@docker-compose down
	@echo "$(GREEN)✓ 所有服务已停止$(RESET)"

docker-logs: ## 查看 Docker 日志
	@docker-compose logs -f

clean: ## 清理临时文件和缓存
	@echo "$(BLUE)清理临时文件...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/htmlcov 2>/dev/null || true
	@echo "$(GREEN)✓ 清理完成$(RESET)"

clean-all: clean ## 深度清理（包括虚拟环境和数据库）
	@echo "$(RED)警告: 这将删除虚拟环境和数据库！$(RESET)"
	@read -p "确认继续? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -rf backend/.venv 2>/dev/null || true
	@rm -f backend/oj.db 2>/dev/null || true
	@docker-compose down -v
	@echo "$(GREEN)✓ 深度清理完成$(RESET)"

.PHONY: status
status: ## 显示服务状态
	@echo "$(BLUE)Docker 服务状态:$(RESET)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)后端 API:$(RESET) http://localhost:8000"
	@echo "$(BLUE)API 文档:$(RESET) http://localhost:8000/api/docs"
	@echo "$(BLUE)前端应用:$(RESET) http://localhost:3000"
