#!make
repo ?= "mirrors.tencent.com/bk-honor"
version ?= "open-source"
platform ?= "linux/amd64,linux/arm64"
listen_port ?= "8009"
dev_env_file ?= "src/api/bk_honor/settings/.env"


build:
	docker build .  -t ${repo}/bk-honor:${version}

push:
	docker push ${repo}/bk-honor:${version}

buildx:
	docker buildx build . --platform ${platform} -t ${repo}/bk-honor:${version} --push

makemigrations:
	export DJANGO_SETTINGS_MODULE="bk_honor.settings.overlays.dev" && \
	cd src/api && poetry run python manage.py makemigrations

migrate:
	export DJANGO_SETTINGS_MODULE="bk_honor.settings.overlays.dev" && \
	cd src/api && poetry run python manage.py migrate

test:
	cd src/api && pytest --disable-pytest-warnings --reuse-db

load:
	export DJANGO_SETTINGS_MODULE="bk_honor.settings.overlays.dev" && \
		cd src/api && poetry run python manage.py load_policies_from_yaml

generate-db-graph:
	cd src/api && poetry run python manage.py graph_models awards -o docs/_images/db.png

run-backend:
	export DJANGO_SETTINGS_MODULE="bk_honor.settings.overlays.dev" && \
	cd src/api && poetry run python manage.py runserver 0.0.0.0:${listen_port}

run:
	mkdir -p .services/
	docker pull ${repo}/bk-honor:${version}

	STORAGE_ROOT=.services/ MYSQL_ROOT_PASSWORD=123456 REPO=${repo} TAG=${version} PORT=${listen_port}  \
	docker-compose --env-file ${dev_env_file} -f docker-compose.yaml up -d

stop:
	STORAGE_ROOT=.services/ MYSQL_ROOT_PASSWORD=123456 REPO=${repo} TAG=${version} PORT=${listen_port} \
	docker-compose --env-file ${dev_env_file} -f docker-compose.yaml down

start: build run

startx: buildx run
