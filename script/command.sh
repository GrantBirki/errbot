#!/bin/bash

# Exit if any commands fails
set -e

OFF='\033[0m' # Text color Reset
BLUE='\033[0;34m' # Blue
GREEN='\033[0;32m' # Green

# Read the input
read -p "[?] Please enter the name of the command you wish to create: " command_name

# Force it as lowercase
command_name="${command_name,,}"

# Dirs to copy from and to
TEMPLATE_DIR_SRC="template"
TEMPLATE_DIR_DST="app/plugins/$command_name"

# Check if the directory already exists
if [[ -d "$TEMPLATE_DIR_DST" ]]
then
    echo -e "$BLUE[i]$OFF INFO: $TEMPLATE_DIR_DST already exists! Please rename this directory, remove it, or choose a different name. Exiting..."
    exit 0
fi

# Copy template folder
echo -e "$BLUE[i]$OFF Copying: $TEMPLATE_DIR_SRC -> $TEMPLATE_DIR_DST..."

if cp -r $TEMPLATE_DIR_SRC $TEMPLATE_DIR_DST ; then
    echo -e "$GREEN[i]$OFF OK: Created new directory with your command: $TEMPLATE_DIR_DST"
else
    echo -e "$BLUE[!]$OFF Command failed"
fi

# Renames files to command_name
echo -e "$BLUE[i]$OFF Updating copied files with your new command..."
mv "$TEMPLATE_DIR_DST/template.plug" "$TEMPLATE_DIR_DST/$command_name.plug"
mv "$TEMPLATE_DIR_DST/template.py" "$TEMPLATE_DIR_DST/$command_name.py"

# Removes '#Change me!' strings
find $TEMPLATE_DIR_DST -type f | xargs sed -i 's/# Change me!//g'
# Updates Template/template strings
command_name_upper=${command_name^}
find $TEMPLATE_DIR_DST -type f | xargs sed -i "s/Template/$command_name_upper/g"
find $TEMPLATE_DIR_DST -type f | xargs sed -i "s/template/$command_name/g"

echo -e "✅ OK: All done! Check out your new command directory:$BLUE $TEMPLATE_DIR_DST $OFF"