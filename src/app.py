from flask import Flask, request, abort
from util import gh_event_source_is_valid
from github import Github
import json
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # maybe this should tell us something useful
        # like "bugflow is great, see the web site"
        return "OK", 200

    elif request.method == 'POST':
        # print(request.headers.get('X-GitHub-Event'), file=sys.stdout)
        # We only accept callbacks from GitHub or localhost
        if not gh_event_source_is_valid(request.remote_addr):
            abort(403)

        # FIXME: validate the sig header
        event_header = request.headers.get('X-Hub-Signature')
        # FIXME: write a good log message
        event_guid = request.headers.get('X-GitHub-Delivery')
        event_type = request.headers.get('X-GitHub-Event')
        
        # get the config file for the source repository
        # ...
        try:
            payload=json.loads(request.data)
            # eyeball the payload and try to find the source repo...
            print(json.dumps(payload, sort_keys=True, indent=4),
                  file=sys.stdout)
        except json.JSONDecodeError:
            msg = "unable to parse payload json"
            print (msg, file=sys.stdout)
            return msg, 400
        
        # TODO FIXME WIP
        # dispatch a worker for each configured policy
        # process the callback...
        #
        # FIXME: maybe refactor everything to use PubSubHubHub?
        # TODO: figure out what kind of response is appropriate
        return json.dumps({'msg': 'thanks for that'}), 200
    else:
        return "not a supported method", 400


if __name__ == '__main__':
    app.run()
