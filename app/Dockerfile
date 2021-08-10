FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
RUN errbot --init

RUN apt-get update -y && apt-get install dnsutils -y

# cleanup unused default errbot plugins
RUN rm -rf plugins/err-example
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/chatRoom.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/flows.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/webserver.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/backup.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/plugins.*
RUN rm /usr/local/lib/python3.9/site-packages/errbot/core_plugins/textcmds.*

# For DISCORD
COPY backend /app/backend
RUN pip install -r /app/backend/err-backend-discord/requirements.txt

# copy local files
COPY config.py /app/config.py
COPY plugins /app/plugins

ENTRYPOINT ["errbot", "-c", "/app/config.py"]
