# RedstoneReporter Makefile

.PHONY: help install run test docker-build docker-up docker-down docker-logs clean

help:
	@echo "RedstoneReporter - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make run           - Run the application locally"
	@echo "  make test          - Run test suite"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start with docker-compose (build + run)"
	@echo "  make docker-down   - Stop docker-compose"
	@echo "  make docker-logs   - View docker logs"
	@echo "  make docker-shell  - Open shell in running container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove generated files and caches"

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest -v tests/

docker-build:
	docker-compose build

docker-up:
	docker-compose up --build -d
	@echo ""
	@echo "✅ RedstoneReporter running at http://localhost:8000"
	@echo "📊 Dashboard: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "View logs: make docker-logs"
	@echo "Stop: make docker-down"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec redstone-reporter /bin/bash

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage
	@echo "✨ Cleanup completed"

# Git helpers
.PHONY: git-status git-add git-commit

git-status:
	git status

git-add:
	git add .

git-commit:
	@read -p "Commit message: " msg; \
	git commit -m "$$msg"
