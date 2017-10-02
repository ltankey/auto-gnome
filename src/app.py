from flask import Flask, request, abort
from github import Github
import json
import requests
import sys
import yaml
from util import (
    gh_event_source_is_valid,
    Config,
    CallbackEvent
)
from gh import EventSourceValidator

# verbose logging
# FIXME: DEBUG should be coming from the environment
DEBUG=True

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

        # FIXME: push any header stuff into CallbackEvent class
        # FIXME: validate the sig header
        event_header = request.headers.get('X-Hub-Signature')
        # FIXME: write a good log message
        event_guid = request.headers.get('X-GitHub-Delivery')
        event_type = request.headers.get('X-GitHub-Event')
        
        cbe = CallbackEvent(request)
        if not cbe.is_valid():
            msg = "callback payload does not appear valid"
            print (msg, file=sys.stdout)
            return msg, 400

        config = Config(cbe)
        for activity in config.get_activities():
            activity.dispatch_gnome()

        # FIXME: maybe refactor everything to use PubSubHubHub?
        # TODO: figure out what kind of response is appropriate
        return json.dumps({'msg': 'thanks for that'}), 200
    else:
        return "not a supported method", 400


if __name__ == '__main__':
    app.run()

