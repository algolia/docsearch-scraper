#! /bin/sh

if [ $# -lt 1 ]; then
    USE_PYTHON3=false
else
    USE_PYTHON3=`[ $1 = true ] && echo true || echo false`
fi

if $USE_PYTHON3; then
    apt-get update -y && apt-get install -y python3-dev
fi

pip install -U pip
pip install virtualenv

if $USE_PYTHON3; then
    virtualenv venv -p python3
else
    virtualenv venv
fi

. venv/bin/activate

pip install -U pip
pip install -r requirements.txt
