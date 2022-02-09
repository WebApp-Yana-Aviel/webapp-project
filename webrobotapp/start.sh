#!/bin/bash
cd /home/webrgacv/webrobotapp
source /home/webrgacv/webrobotapp/auth/bin/activate
export FLASK_APP=run.py
export FLASK_DEBUG=False
export FLASK_ENV=production
export APP_CONFIG_FILE=config.py
python telebot.py &
python temperature_raspberry.py &

flask run
