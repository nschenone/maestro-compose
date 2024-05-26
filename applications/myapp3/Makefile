.PHONY: help

help:
	@echo "Usage:"
	@echo "    up:       Start app"
	@echo "    down:     Stop app"
	@echo "    upgrade   Upgrade version"
	@echo "    restart:  Restart app"

up:
	docker compose up -d

down:
	docker compose down

restart: down up

update:
	docker compose pull

upgrade: update up
