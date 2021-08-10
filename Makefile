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
	docker run -it --rm --env-file config.env -e LOCAL_TESTING=True errbot-launchpad_chatbot
	@echo "\e[32m[#] Exiting and cleaning up :)\e[0m"

discord:
	script/discord.sh
