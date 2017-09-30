from flask import Flask, request, abort
from github import Github
import json
import requests
import sys
import yaml
from util import (
    gh_event_source_is_valid,
)
import policies

# verbose logging
DEBUG=True

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


class Config(object):
    def __init__(self, callback):
        self.callback = callback
        self.payload= callback.payload()
        self._yaml=None

    def get_yaml(self):
        if self._yaml:
            return self._yaml
        # first, call the contents API to get the file metadata
        contents_url_payload = self.payload['contents_url']
        contents_template = str(contents_url_payload).replace('{+path}','{}')
        contents_url = contents_template.format('.gnome.yml')
        contents = requests.get(contents_url).json()
        # then, from the metadata, get the file itself
        #
        # FIXME: this double-tap is lame
        # maybe we should only do the double-tap after a heuristic guess
        # fails
        gnome_yml = requests.get(contents['download_url']).text
        # FIXME: validate the yaml
        self._yaml = gnome_yml
        return gnome_yml

    def get_activities(self):
        gnome_yaml = yaml.load(self.get_yaml())
        activities = []
        bad_news = []
        # stub
        #policies =(DumbPolicy(self.callback),)

        for policy_name in gnome_yaml['policies']:
            # DEBUG
            print(policy_name, file=sys.stdout)
            if policy_name not in dir(policies):
                bad_news.append((policy_name, "not found"))
            elif policy_name == "Policy":
                bad_news.append((policy_name, "forbidden"))
            else:
                # auto-flagilate for use of eval
                policy_class = eval('policies.{}'.format(policy_name))
                activities.append(policy_class(self.callback))
        if len(bad_news)>0:
            #do something with the bad news
            print("BAD NEWS: {}".format(bad_news), file=sys.stdout)
        # and we have a module containing all the policy classes
        # and all the policy classes provide a dispatch_gnome method
        return activities


class InvalidPayloadJSONError(Exception): pass


class CallbackEvent(object):
    def __init__(self, request):
        self.request = request
        self._payload=None

    def payload(self):
        # try the fast way
        if self._payload:
            return self._payload
        # then try the slow way
        data = self.request.data
        try:
            payload=json.loads(data)
            self._payload = payload
            return payload
        except json.JSONDecodeError:
            raise InvalidPayloadJSONError()

    def is_valid(self):
        try:
            p = self.payload()
            if not 'contents_url' in p:
                if DEBUG:
                    msg = "payload does not contain a contents_url"
                    print(msg, file=sys.stdout)
                    print(json.dumps(p, indent=4), file=sys.stdout)
                return False
            return True
        except InvalidPayloadJSONError:
            return False

if __name__ == '__main__':
    app.run()

