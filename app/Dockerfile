FROM python:3.9

WORKDIR /app

# install dependencies
RUN apt update -y && apt upgrade -y
RUN apt install ffmpeg -y

# setup errbot base
COPY requirements.txt .
RUN pip install -r requirements.txt

# create nonroot errbot user and switch to it
RUN useradd -m errbot
RUN chown -R errbot:errbot /app
RUN chown -R errbot:errbot /usr/local/lib/python3.9/site-packages/errbot
USER errbot

# init errbot
RUN errbot --init

# cleanup unused default errbot plugins
RUN rm -rf plugins/err-example \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/chatRoom.* \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/flows.* \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/webserver.* \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/backup.* \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/plugins.* \
rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/textcmds.*

# for discord / other backends
COPY --chown=errbot:errbot backend /app/backend
RUN pip install -r /app/backend/err-backend-discord/requirements.txt

# copy local files
COPY --chown=errbot:errbot config.py /app/config.py
COPY --chown=errbot:errbot plugins /app/plugins

ENTRYPOINT ["errbot", "-c", "/app/config.py"]
