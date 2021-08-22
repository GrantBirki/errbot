#!/bin/bash

TEMPLATE_DIR_SRC="template"
TEMPLATE_DIR_DST="app/plugins/template"

if [[ -d "$TEMPLATE_DIR_DST" ]]
then
    echo "INFO: $TEMPLATE_DIR_DST already exists. Please rename this directory or remove it. Exiting..."
    exit 0
fi

echo "Copying: $TEMPLATE_DIR_SRC -> $TEMPLATE_DIR_DST"

if cp -r $TEMPLATE_DIR_SRC $TEMPLATE_DIR_DST ; then
    echo "OK: Copied template to the $TEMPLATE_DIR_DST folder. Enter this folder and edit all the lines that say '# change me!'"
else
    echo "Command failed"
fi
