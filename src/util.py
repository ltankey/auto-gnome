import json
import sys
import yaml
import os
import requests
import ipaddress
from github import Github
from gh import Repo

import policies


# FIXME: DEBUG should be comming from the environment!!!
DEBUG=True

GITHUB_SPECIAL_HEADERS = ('X-Hub-Signature',
                          'X-GitHub-Delivery',
                          'X-GitHub-Event')

# FIXME: elaborate on list of forbidden policy names
# "Policy" is the abstract base class defined in policies.__init__.py
# We should probably prohibit all the __builtins__ and other python
# reserved words, becuase havok.
#
# we must be extra careful because of eval
FORBIDDEN_POLICY_NAMES = ("Policy",)


# FIXME: use a cache (all over the place)

class InvalidPayloadJSONError(Exception): pass


class Config(object):
    """
    Config is generated from the .gnome.yml file that is found in the root
    of a repository that is a source of GitHub callback events.

    The .gnome.yml file is retrieved, parsed and validated. Then, the
    get_activities() method can be used to instantiate policy objects for
    everything that was configured in the repo.
    """
    def __init__(self, repo_name=None, callback=None):
        self.callback = callback
        if repo_name:
            self.repo_name = repo_name
        else:
            self.repo_name = callback.payload()['repository']['full_name']
        self._yaml = None

    def get_yaml(self):
        if self._yaml:
            return self._yaml

        self._yaml =  Repo(self.repo_name).get_config()
        return self._yaml


    def get_activities(self):
        """
        This is the magic method. It processes the config (from .gnome.yml)
        and instantiates the policies, which are presumably dispatched.
        """
        activities = []
        bad_news = []
        if not self.yaml_is_valid():
            # FIXME: figure out what to do without valid config
            raise Exception("debug this please")

        # FIXME: maybe nicer if get_yaml returned parsed yaml
        # rather than string (and be named differently)
        parsed_yml = self.get_yaml()

        for policy_name in parsed_yml['policies']:
            if policy_name in FORBIDDEN_POLICY_NAMES:
                bad_news.append((policy_name, "forbidden"))
            elif policy_name not in policies.MANIFEST.keys():
                bad_news.append((policy_name, "not found"))
            else:
                policy_class = policies.MANIFEST.get(policy_name, None)
                activities.append(policy_class(self, self.callback))

        if len(bad_news) > 0:
            # FIXME: do something smarter with bad news
            # maybe a BadNewsProcessor, that makes information
            # available to the repo owner/subscriber.
            msg = "BAD NEWS: {}".format(bad_news)
            print(msg, file=sys.stdout)

        return activities

    def yaml_is_valid(self):
        parsed_yml = self.get_yaml()
        if 'policies' not in parsed_yml:
            if DEBUG:
                msg = "policies not in parsed yaml"
                print(msg, file=sys.stdout)
                print(parsed_yml, file=sys.stdout)
            return False
        return True

class CallbackEvent(object):
    """
    CallbackEvent is an abstraction over the raw flask request object.
    It provides convenience methods for validation and payload access.
    """
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

    def headers(self):
        headers = {}
        for k in GITHUB_SPECIAL_HEADERS:
            try:
                headers[k]=self.request.headers.get(k)
            except:
                pass
        return headers

    def is_valid(self):
        headers = self.headers()
        for h in GITHUB_SPECIAL_HEADERS:
            if h not in headers:
                return False
        # FIXME: unit-test coverage for callback validation required
        try:
            p = self.payload()
            if not 'repository' in p:
                if DEBUG:
                    msg = "payload does not contain a repository"
                    print(msg, file=sys.stdout)
                    print(json.dumps(p, indent=4), file=sys.stdout)
                return False
            repo_data = p['repository']
            if 'full_name' not in repo_data:
                if DEBUG:
                    msg = "repo_data does not have a full_name"
                    print(msg, file=sys.stdout)
                    print(json.dumps(repo_data, indent=4), file=sys.stdout)
                return False
            return True
        except InvalidPayloadJSONError:
            return False
