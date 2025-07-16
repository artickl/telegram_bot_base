#!/bin/bash

screen_name="telegram_bot_base"

screen -list \
    | grep $screen_name \
    | while read screen_line; do
        #screen_item = "echo $(echo $screen_line | awk {'print $1'})"
        echo "killing old session: $screen_line"
        screen -S "$(echo $screen_line | awk {'print $1'})" -X quit
    done

cd "$(dirname "$0")"
screen -S $screen_name -dm bash -c "source tbb/bin/activate; python3 app.py; sleep 10;"

screen -list \
    | grep $screen_name \
    | while read screen_line; do
        echo "started new session: $screen_line"
    done