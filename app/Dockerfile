FROM python:3.9-slim

WORKDIR /app

# install dependencies
RUN apt-get update -y && apt-get install dnsutils -y

# setup errbot base
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN errbot --init

# for discord / other backends
COPY backend /app/backend
RUN pip install -r /app/backend/err-backend-discord/requirements.txt

# cleanup unused default errbot plugins
RUN rm -rf plugins/err-example
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/chatRoom.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/flows.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/webserver.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/backup.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/plugins.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/textcmds.*

# copy local files
COPY config.py /app/config.py
COPY plugins /app/plugins

ENTRYPOINT ["errbot", "-c", "/app/config.py"]
