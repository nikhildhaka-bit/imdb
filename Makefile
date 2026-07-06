.DEFAULT_GOAL := help

BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV_PY := $(BACKEND_DIR)/venv/Scripts/python.exe
VENV_UVICORN := $(BACKEND_DIR)/venv/Scripts/uvicorn.exe
VENV_ALEMBIC := $(BACKEND_DIR)/venv/Scripts/alembic.exe

.PHONY: help install install-backend install-frontend backend frontend run migrate revision clean

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install backend + frontend dependencies

install-backend: ## Install backend dependencies into backend/venv
	cd $(BACKEND_DIR) && python -m venv venv
	$(VENV_PY) -m pip install -r $(BACKEND_DIR)/requirements.txt

install-frontend: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

backend: ## Run the FastAPI backend (http://localhost:8001)
	cd $(BACKEND_DIR) && ../$(VENV_UVICORN) main:app --reload --port 8001

frontend: ## Run the Vite dev server (http://localhost:5173)
	cd $(FRONTEND_DIR) && npm run dev

run: ## Run backend + frontend together
	$(MAKE) -j2 backend frontend

migrate: ## Apply database migrations
	cd $(BACKEND_DIR) && ../$(VENV_ALEMBIC) upgrade head

revision: ## Create a new alembic migration (usage: make revision m="message")
	cd $(BACKEND_DIR) && ../$(VENV_ALEMBIC) revision --autogenerate -m "$(m)"

clean: ## Remove Python/Node caches
	find . -type d -name "__pycache__" -not -path "*/venv/*" -not -path "*/node_modules/*" -exec rm -rf {} +
