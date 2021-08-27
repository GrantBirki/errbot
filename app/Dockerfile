FROM python:3.9-slim

WORKDIR /app

# install dependencies
RUN apt update -y && apt upgrade -y

# setup errbot base
COPY requirements.txt .
RUN pip install -r requirements.txt

# cleanup unused default errbot plugins
RUN rm -rf plugins/err-example
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/chatRoom.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/flows.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/webserver.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/backup.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/plugins.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/textcmds.*

# create nonroot errbot user and switch to it
RUN useradd -m errbot
RUN chown -R errbot:errbot /app
USER errbot

# init errbot
RUN errbot --init

# for discord / other backends
COPY --chown=errbot:errbot backend /app/backend
RUN pip install -r /app/backend/err-backend-discord/requirements.txt

# copy local files
COPY --chown=errbot:errbot config.py /app/config.py
COPY --chown=errbot:errbot plugins /app/plugins

ENTRYPOINT ["errbot", "-c", "/app/config.py"]
