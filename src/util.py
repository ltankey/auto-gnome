import json
import sys
import yaml
import os
import requests
import ipaddress
from github import Github

import policies


# FIXME: DEBUG should be comming from the environment!!!
DEBUG=True

# FIXME: elaborate on list of forbidden policy names
# "Policy" is the abstract base class defined in policies.__init__.py
# We should probably prohibit all the __builtins__ and other python
# reserved words, becuase havok.
#
# we must be extra careful because of eval
FORBIDDEN_POLICY_NAMES = ("Policy",)


# FIXME: use a cache (all over the place)

def gh_event_source_is_valid(ip_str):
    """
    GitHub publishes the address ranges that they make callbacks from.

    This function returns true if the IP address (string) passed to it
    is within the whitelisted address range published by GitHub.
    """
    request_ip = ipaddress.ip_address(u'{0}'.format(ip_str))
    # TODO: consider only doing this id DEBUG==True ???
    if str(request_ip) == '127.0.0.1':
        return True    
    # TODO: cache the hook_blocks
    hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
    for block in hook_blocks:
        if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
            return True
    return False


# FIXME: create method to validate the HMAC signature header
"""
GH is kind enough to sign the callback payloads, and put the HMAC sig
in a header. It is signed with the secret configured in the web hook.

It only makes sense for us to validate this signature if we tell our users
to confgure the web hook with a signature we know. Since it wouldn't make
sense to put a shared secret in the .gnome.yml, we should probably either
ignore this, OR provide a sign-up process and a web site, wher we generate
the secret and tell our users to put it in the GH callback config.

Until then (do we need to bother?), we can ignore the HMAC sig.
"""

class InvalidPayloadJSONError(Exception): pass


class Config(object):
    """
    Config is generated from the .gnome.yml file that is found in the root
    of a repository that is a source of GitHub callback events.
    
    The .gnome.yml file is retrieved, parsed and validated. Then, the
    get_activities() method can be used to instantiate policy objects for
    everything that was configured in the repo.
    """
    def __init__(self, callback):
        self.callback = callback
        self.payload= callback.payload()
        self._yaml=None

    def get_yaml(self):
        if self._yaml:
            return self._yaml
        # TODO: figure out what do we do about branches
        # FIXME: always use the appropriate branch
        branch="master"
        url_template = "https://raw.githubusercontent.com/{}/{}/.gnome.yml"
        repo_fullname = self.payload['repository']['full_name']
        url = url_template.format(repo_fullname, branch)
        raw_yml = requests.get(url).text
        # FIXME: handle non-200 codes
        # TODO: decide if we should be iterating over 404s/config file names
        # FIXME: validate the yaml
        self._yaml = raw_yml
        return raw_yml

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
        
        # FIXME: get_yaml should return parsed yaml (and be named differently)
        parsed_yml = yaml.load(self.get_yaml())

        for policy_name in parsed_yml['policies']:
            if policy_name in FORBIDDEN_POLICY_NAMES:
                bad_news.append((policy_name, "forbidden"))  
            elif policy_name not in dir(policies):
                bad_news.append((policy_name, "not found"))
            else:
                # TODO: auto-flagilate for use of eval, for shame!
                policy_class = eval('policies.{}'.format(policy_name))
                # FIXME: detect and respond to invalid policy classes
                # (policy classes must have a dispatch_gnome method)
                activities.append(policy_class(self.callback))

        if len(bad_news) > 0:
            # FIXME: do something smarter with bad news
            # maybe a BadNewsProcessor?
            # or just conventional logging
            msg = "BAD NEWS: {}".format(bad_news)
            print(msg, file=sys.stdout)

        return activities

    def yaml_is_valid(self):
        raw_yml = self.get_yaml()
        parsed_yml =yaml.load(raw_yml)
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
            # there is something wrong about doing this here,
            # rather than in the validation method
            raise InvalidPayloadJSONError()

    def is_valid(self):
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


if __name__ == "__main__":
    print("TODO: make tests suite")

