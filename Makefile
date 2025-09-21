APP_NAME := $(shell python metadata.py name)
APP_VERSION := $(shell python metadata.py version)
IMAGE_NAME := demsking/$(APP_NAME)

# Start the development environment using tmuxinator
shell:
	tmuxinator

stop:
	tmux kill-session -t traefik-http-proxy

install:
	poetry install

up:
	docker compose up --build -d --remove-orphans

restart:
	docker compose restart

watch:
	docker compose watch server

down:
	docker compose down

config:
	docker compose config

logs:
	docker compose logs -f

ps:
	docker compose ps

stats:
	docker compose stats

gen-tests:
	python gen.py
	pre-commit run double-quote-string-fixer

test: gen-tests
	pytest -vv

coverage: gen-tests
	pytest --cov=server

coverage-html: gen-tests
	pytest --cov=server --cov-report=html

open-docs:
	open http://localhost:56116/docs

lint:
	pre-commit run --all-files

fix:
	ruff check . --fix

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated

update:
	poetry -C python update
	devbox update
	pre-commit autoupdate

clean:
	rm -rf dist/

#
## Packaging
build/context:
	docker buildx create --name $(APP_NAME) --bootstrap
	mkdir -p build/
	touch $@

multiplatform-image: build/context
	docker buildx use $(APP_NAME)
	docker buildx build . \
	  --platform linux/amd64,linux/arm64 \
	  --push \
	  --progress plain \
	  --tag $(IMAGE_NAME):$(APP_VERSION) \
	  --tag $(IMAGE_NAME):latest \
	  --build-arg APP_NAME=$(APP_NAME) \
	  --build-arg APP_VERSION=$(APP_VERSION) \
	  --label "org.opencontainers.image.title=$(APP_NAME)" \
	  --label "org.opencontainers.image.description=$(shell python metadata.py description)" \
	  --label "org.opencontainers.image.version=$(APP_VERSION)" \
	  --label "org.opencontainers.image.revision=$(shell git rev-parse HEAD)" \
	  --label "org.opencontainers.image.authors=$(shell python metadata.py authors)" \
	  --label "org.opencontainers.image.created=$(shell date --rfc-3339=seconds)" \
	  --label "org.opencontainers.image.source=$(shell python metadata.py repository)" \
	  --label "org.opencontainers.image.url=$(shell python metadata.py repository)" \
	  --label "org.opencontainers.image.documentation=$(shell python metadata.py documentation)" \
	  --label "org.opencontainers.image.vendor=Sébastien Demanou" \
	  --label "org.opencontainers.image.licenses=$(shell python metadata.py license)"

image-test:
	docker build . \
	  --progress plain \
	  --tag $(IMAGE_NAME):test \
	  --build-arg APP_NAME=$(APP_NAME) \
	  --build-arg APP_VERSION=$(APP_VERSION)

exec:
	docker run -it --rm -p 6116:6116 -v DATA_PATH=/tmp $(IMAGE_NAME):test

publish: image-test doc
	git commit pyproject.toml doc/ -m "Release $(APP_VERSION)"
	$(MAKE) multiplatform-image
	git tag v$(APP_VERSION)
	git push --tags origin main
