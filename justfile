# LockIner - Just commands

# Show this help
default:
    @just --list

# Start the application
up:
    @echo "🚀 Starting LockIner..."
    docker-compose up -d
    @echo "✅ Application started!"
    @echo "  Frontend: http://localhost:3000"
    @echo "  Backend:  http://localhost:8000"
    @echo "  API Docs: http://localhost:8000/docs"

# Stop the application
down:
    @echo "⏹️  Stopping LockIner..."
    docker-compose down
    @echo "✅ Application stopped"

# Restart the application
restart: down up

# Show logs (tail -f)
logs:
    docker-compose logs -f

# Show backend logs only
logs-backend:
    docker-compose logs -f backend

# Show frontend logs only
logs-frontend:
    docker-compose logs -f frontend

# Build Docker images from scratch
build:
    @echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    @echo "✅ Build complete"

# Initialize project (first time setup)
init:
    @echo "🎉 Initializing LockIner..."
    @if [ ! -f .env ]; then \
        cp .env.example .env; \
        echo "✅ Created .env file (fill in your API keys!)"; \
    else \
        echo "⚠️  .env already exists"; \
    fi
    @mkdir -p backend/data backend/uploads backups
    @echo "✅ Created data directories"
    @echo "🔨 Building containers..."
    docker-compose build
    @echo "✅ Project initialized!"
    @echo ""
    @echo "Next steps:"
    @echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
    @echo "  2. Run: just up"
    @echo "  3. Visit: http://localhost:3000"

# Clean everything (containers, volumes, images) - DANGEROUS!
clean:
    @echo "⚠️  This will delete ALL data, containers, and volumes!"
    @read -p "Are you sure? [y/N] " confirm; \
    if [ "$$confirm" = "y" ]; then \
        docker-compose down -v --rmi all; \
        rm -rf backend/data/* backend/uploads/*; \
        echo "✅ Cleanup complete"; \
    else \
        echo "❌ Cancelled"; \
    fi

# Backup the SQLite database
backup:
    @echo "💾 Creating database backup..."
    @mkdir -p backups
    @timestamp=$$(date +%Y%m%d_%H%M%S); \
    docker-compose exec backend sqlite3 /data/scrooge.db ".backup /data/backup_$$timestamp.db"; \
    docker cp scrooge-backend:/data/backup_$$timestamp.db ./backups/; \
    docker-compose exec backend rm /data/backup_$$timestamp.db; \
    echo "✅ Backup saved to: backups/backup_$$timestamp.db"

# Restore database from backup (usage: just restore backup_20250110.db)
restore BACKUP_FILE:
    @echo "📥 Restoring from: {{BACKUP_FILE}}"
    docker cp ./backups/{{BACKUP_FILE}} scrooge-backend:/data/restore.db
    docker-compose exec backend mv /data/restore.db /data/scrooge.db
    @echo "✅ Database restored"

# Open bash shell in backend container
shell-backend:
    docker-compose exec backend /bin/bash

# Open sh shell in frontend container
shell-frontend:
    docker-compose exec frontend /bin/sh

# Open SQLite interactive shell
db-shell:
    docker-compose exec backend sqlite3 /data/scrooge.db

# Run backend tests (pytest)
test-backend:
    docker-compose exec -e PYTHONPATH=/app backend pytest -v

# Run frontend tests (vitest)
test-frontend:
    docker-compose exec frontend npm run test

# Show container status
ps:
    docker-compose ps

# Show resource usage stats
stats:
    docker stats scrooge-backend scrooge-frontend

# Clean unused Docker resources
prune:
    docker system prune -f
    @echo "✅ Docker cleanup complete"

# Follow logs for all services with color
logs-all:
    docker-compose logs -f --tail=100

# Rebuild and restart a specific service (usage: just rebuild backend)
rebuild SERVICE:
    docker-compose build {{SERVICE}}
    docker-compose up -d {{SERVICE}}
    @echo "✅ Rebuilt {{SERVICE}}"

# Run database migrations (TODO: implement)
migrate:
    @echo "🔄 Running database migrations..."
    docker-compose exec backend python app/init_db.py
    @echo "✅ Migrations complete"

# Seed database with example data (TODO: implement)
seed:
    @echo "🌱 Seeding database..."
    docker-compose exec backend python app/seed.py
    @echo "✅ Database seeded"

# Check if application is healthy
health:
    @echo "🏥 Checking application health..."
    @curl -f http://localhost:8000/health && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"
    @curl -f http://localhost:3000 && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"

# Open API documentation in browser
docs:
    @echo "📚 Opening API docs..."
    @open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Visit: http://localhost:8000/docs"

# Open frontend in browser
open:
    @echo "🌐 Opening frontend..."
    @open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Visit: http://localhost:3000"

# Full reset: clean, init, up
reset: clean init up

# Quick dev setup (for daily work)
dev: up logs

# Production build (TODO: optimize for production)
prod:
    @echo "🚀 Building for production..."
    @echo "⚠️  Not implemented yet"
