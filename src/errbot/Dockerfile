FROM python:3.9-alpine

WORKDIR /app

# install alpine dependencies
RUN apk update && apk upgrade
RUN apk add gcc musl-dev libffi-dev make libffi-dev libsodium-dev opus-dev ffmpeg zlib-dev jpeg-dev

# setup selenium
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories
RUN apk update
RUN apk add chromium chromium-chromedriver xvfb

# install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# create nonroot errbot user and switch to it
RUN adduser -D errbot
RUN chown -R errbot:errbot /app
RUN chown -R errbot:errbot /usr/local/lib/python3.9/site-packages/errbot
USER errbot

# replace default errbot files with our custom ones
COPY --chown=errbot:errbot package/core.py /usr/local/lib/python3.9/site-packages/errbot/core.py

# init errbot
RUN errbot --init

# cleanup unused default errbot plugins
RUN \
rm -rf plugins/err-example \
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
