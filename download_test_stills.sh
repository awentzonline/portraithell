#!/bin/bash

if [ -z "$1" -o -z "$2" ]
then
    echo "Usage: this.sh <port|land> <youtube_id>"
    exit 1
fi
mkdir -p ./tests/imgs/$1/$2
curl -o ./tests/imgs/$1/$2/1.jpg http://img.youtube.com/vi/$2/1.jpg
curl -o ./tests/imgs/$1/$2/2.jpg http://img.youtube.com/vi/$2/2.jpg
curl -o ./tests/imgs/$1/$2/3.jpg http://img.youtube.com/vi/$2/3.jpg
