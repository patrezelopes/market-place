.DEFAULT_GOAL := all

COMPOSE=docker-compose $(COMPOSE_OPTS)


# target: help - display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: up-db - Starts db
up-db:
	$(COMPOSE) up -d market-db

# target: up-api - Starts api
up-api:
	$(COMPOSE) up -d market-api

#Starts all apps
start: up-db up-api

# target: all
up-all:
	$(COMPOSE) up --build -d

# target: stop - Stop all apps
down:
	$(COMPOSE) stop

stop: down

# target: build - Builds docker images
build-no-cache:
	$(COMPOSE) build --no-cache

# target: bash - Runs /bin/bash in App container for development
bash:
	$(COMPOSE) exec api bash

# target: bash - Runs /bin/bash python tests
test:
	$(COMPOSE) exec api bash -c "python manage.py test -v 3"

# target: clean - Stops and removes all containers
clean:
	$(COMPOSE) down -v

# target: logs - Shows logs for db, frontend and app
logs-all:
	$(COMPOSE) logs --follow

logs-api:
	$(COMPOSE) logs -f api

logs-db:
	$(COMPOSE) logs -f api