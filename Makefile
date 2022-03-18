run:
	@echo "\033[0;34m[#] Killing old docker processes\033[0m"
	docker-compose down -v -t 1

	@echo "\033[0;34m[#] Building docker containers - full errbot stack\033[0m"
	docker-compose up --build -d

	@echo "\e[32m[#] Containers are now running!\e[0m"


local:
	@echo "\033[0;34m[#] Starting local bot test environment\033[0m"
	@echo "\033[0;34m[#] Killing old docker processes\033[0m"
	docker-compose down -v -t 1

	@echo "\033[0;34m[#] Building and docker containers\033[0m"
	LOCAL_TESTING=True docker-compose build
	@echo "\e[32m[#] Interact with me over the CLI prompt below\e[0m"
	LOCAL_TESTING=True docker-compose run chatbot
	@echo "\e[32m[#] Exiting and cleaning up :)\e[0m"
	docker-compose down -v -t 1

kube: # start a local minikube cluster for development
	script/local-minikube

discord: # Gets the backend files for discord if they do not exist
	script/discord.sh

command: # Use me to create a new command for the bot from scratch! Just follow the prompts - EX: 'make command'
	script/command.sh

push-azure: # Builds and pushes image to azure - testing only
	@az acr login -n errbot
	@cd app && docker build -t errbot.azurecr.io/errbot:ci-test .
	@docker push errbot.azurecr.io/errbot:ci-test

slides: # Start the slide demo presentation
	cd demo && npm run dev
