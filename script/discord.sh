#!/bin/bash

BACKEND_DIR="app/backend/err-backend-discord"

if [[ -f "$BACKEND_DIR/discord.plug" ]]
then
    echo "OK: $BACKEND_DIR exists and has files! Nothing to do, exiting..."
    exit 0
fi

echo "$BACKEND_DIR does not exist. Let me create that and pull down the necessary files from GitHub for you :)"

mkdir -p $BACKEND_DIR

git clone git@github.com:gbin/err-backend-discord.git $BACKEND_DIR
