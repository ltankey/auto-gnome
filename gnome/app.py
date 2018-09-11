from flask import Flask, request, abort
import json
import sys
from config import settings
from gnome.util import (Config, CallbackEvent)
from gnome.gh import EventSourceValidator

# verbose logging
DEBUG = settings.DEBUG

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # maybe this should tell us something useful
        # like "bugflow is great, see the web site"
        return "OK", 200

    elif request.method == 'POST':
        # We only accept callbacks from GitHub or localhost
        validator = EventSourceValidator()
        if not validator.ip_str_is_valid(request.remote_addr):
            abort(403)

        cbe = CallbackEvent(request)
        if not cbe.is_valid():
            msg = "callback payload does not appear valid"
            print (msg, file=sys.stdout)
            return msg, 400

        config = Config(cbe)
        # TODO: maybe these should be asynchronous
        # maybe even SNS etc...
        for activity in config.get_activities():
            activity.dispatch_gnome()

        # FIXME: maybe refactor everything to use PubSubHubHub?
        # TODO: figure out what kind of response is appropriate
        return json.dumps({'msg': 'thanks for that'}), 200
    else:
        return "not a supported method", 400


if __name__ == '__main__':
    app.run()
