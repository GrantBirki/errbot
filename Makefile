run:
	@echo "\033[0;34m[#] Killing old docker processes\033[0m"
	docker-compose rm -fs

	@echo "\033[0;34m[#] Building docker containers\033[0m"
	docker-compose up --build -d

	@echo "\e[32m[#] Container is now running!\e[0m"

local:
	@echo "\033[0;34m[#] Starting local bot test environment\033[0m"
	@echo "\033[0;34m[#] Killing old docker processes\033[0m"
	docker-compose rm -fs

	@echo "\033[0;34m[#] Building docker containers\033[0m"
	docker-compose build
	@echo "\e[32m[#] TEST Container is now running!\e[0m"
	@echo "\e[32m[#] Interact with me over the CLI prompt below\e[0m"
	docker run -it --rm --env-file config.env --env-file creds.env -e LOCAL_TESTING=True errbot_chatbot:latest
	@echo "\e[32m[#] Exiting and cleaning up :)\e[0m"

discord:
	script/discord.sh

push-azure: # Builds and pushes image to azure - testing only
	@az acr login -n errbot
	@cd app && docker build -t errbot.azurecr.io/errbot:test .
	@docker push errbot.azurecr.io/errbot:test

plan:
	@cd terraform && terraform plan -var-file="terraform.tfvars.json"

apply:
	@cd terraform && terraform apply -var-file="terraform.tfvars.json"

init:
	@cd terraform && terraform init