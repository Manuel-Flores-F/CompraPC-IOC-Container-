#!/bing/bash
. env/bin/activate

export FLASK_APP=test_main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run
