run:
	source ./venv/bin/activate && uvicorn --reload --log-config logging_dev.conf modal_backend.routes.base:app

configure: venv
	source ./venv/bin/activate && pip install -r requirements.dev.txt -r requirements.txt

venv:
	python3.11 -m venv venv

format:
	source ./venv/bin/activate && autoflake -r --in-place --remove-all-unused-imports ./modal_backend
	source ./venv/bin/activate && isort ./modal_backend
	source ./venv/bin/activate && black ./modal_backend
	source ./venv/bin/activate && autoflake -r --in-place --remove-all-unused-imports ./tests
	source ./venv/bin/activate && isort ./tests
	source ./venv/bin/activate && black ./tests
	source ./venv/bin/activate && autoflake -r --in-place --remove-all-unused-imports ./migrations
	source ./venv/bin/activate && isort ./migrations
	source ./venv/bin/activate && black ./migrations

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-modal_backend postgres:15

migrate:
	source ./venv/bin/activate && alembic upgrade head

pytest-container-build:
	 docker build -f Dockerfile.test -t pytest-container .

pytest-container-run:
	 docker run -it \
	 -v /var/run/docker.sock:/var/run/docker.sock \
	 --rm \
	 --add-host host.docker.internal:host-gateway \
	 -e TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal \
	 --network host \
	 pytest-container \
	 $(ARGS)

pytest-rerun:
	docker build -f Dockerfile.test -t pytest-container . \
	&& \
	docker run -it \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--rm \
	--add-host host.docker.internal:host-gateway \
	-e TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal \
	--network host \
	pytest-container \
	$(ARGS)




