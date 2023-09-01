#!/bin/bash

#download node and npm
#curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh ! bash
#. ~/.nvm/nvm.sh
#nvm install node

#create our working directory if it doesn't exists
DIR="/home/ubuntu/nlp-2-sql-01"
if [ -d "$DIR"]; then
    echo "${DIR} directory already exists"
else 
    echo "Creating ${DIR} directory"
    mkdir ${DIR}
fi
