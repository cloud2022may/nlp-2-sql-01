#!/bin/bash

# navigate into our working directory

#cd /home/ubuntu/nlp-2-sql-01

#add npm and node to path
#export NVM_DIR="$HOME/.nvm"
#[ -s "$NVM_DIR/nvm.sh" ] && "$NVM_DIR/nvm.sh"  #loads nvm
#[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  #loads nvm bash_completion (node is in path now)

#install node modules
#npm install

#start our node app in the background
#node app.js > app.out.log 2>app.err.log < /dev/null &

############################ 1 way
# change directory to where the nlptest script is there
cd /home/ubuntu

nohup ./nlptest.sh &

###########################  2nd way
# change directory to where the nlptest script is there
#cd /home/ubuntu/nlp-2-sql-01

#install node modules
#npm install

#python3 -m streamlit run ./navapp.py > navapp.out.log 2>navapp.err.log < /dev/null &