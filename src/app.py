from flask import Flask, request, abort
from util import (
    gh_event_source_is_valid,
)
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
        cbe = CallbackEvent(request)
        if not cbe.is_valid():
            msg = "unable to parse payload json"
            print (msg, file=sys.stdout)
            return msg, 400

        config = Config(cbe)
        for policy in config.get_policies():
            policy.dispatch_gnome()
        
        # FIXME: maybe refactor everything to use PubSubHubHub?
        # TODO: figure out what kind of response is appropriate
        return json.dumps({'msg': 'thanks for that'}), 200
    else:
        return "not a supported method", 400


class Policy(object):
    def __init__(self, callback):
        self.callback=callback


class DumbPolicy(Policy):
    def dispatch_gnome(self):
        print("dumb policy", file=sys.stdout)
        # eyeball the payload
        pl = self.callback.payload()
        js = json.dumps(pl, sort_keys=True, indent=4) 
        print(js, file=sys.stdout)


class Config(object):
    def __init__(self, callback):
        self.callback = callback
        self.payload= callback.payload()
        self._yaml=None

    def get_yaml(self):
        if self._yaml:
            return self._yaml
        return "TODO"

    def get_policies(self):
        yaml = self.get_yaml()
        # TODO: parse the yaml and return pre-configured policy instances
        policies = (
            DumbPolicy(self.callback),
        )
        # something like:
        #
        # policies = []
        # bad_news = []
        # for policy_name in config:
        #     if policy_name not in dir(policy_module):
        #         bad_news.append(policy_name)
        #     else:
        #         policy_module = eval('policy_module.{}'.format(policy_name)
        #         kw_params = config.get_params(policy_name)
        #         policies.append(policy_class(kw_params))
        # if len(bad_news)>0:
        #     do something with the bad news
        # return policies
        #
        # and we have a module containing all the policy classes
        # and all the policy classes provide a dispatch_gnome method
        return policies


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
            self.payload()
            return True
        except InvalidPayloadJSONError:
            return False

if __name__ == '__main__':
    app.run()
