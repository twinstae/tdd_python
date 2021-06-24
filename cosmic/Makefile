export COPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e --timeout=1

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit --timeout=1

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration --timeout=1

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e --timeout=1

logs:
	docker-compose logs --tail=25 api redis_pubsub

black:
	black -l 86 $$(find * -name '*.py')
