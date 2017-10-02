import requests
import ipaddress
from github import Github


# TODO: this should definitely be coming from the environment
import local_secrets
GITHUB_USER = local_secrets.GITHUB_USER
GITHUB_PSX = local_secrets.GITHUB_PSX


class Milestone:
    def open_tickets(self):
        return ()

    
class Issue:
    def has_milestone(self):
        return True
    def move_to_milestone(self, new_milestone):
        pass


# make sure this is lazy
class Repo:
    def ensure_milestone_exists(self, milestone_name, date=None):
        pass
    def ensure_milestone_has_due_date(self, milestone_name, due_date):
        pass


class EventSourceValidator:
    def __init__(self):
        self.hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']

    def ip_str_is_valid(self, ip_str):
        """
        GitHub publishes the address ranges that they make callbacks from.
        
        This function returns true if the IP address (string) passed to it
        is within the whitelisted address range published by GitHub.
        """
        request_ip = ipaddress.ip_address(u'{0}'.format(ip_str))
        if str(request_ip) == '127.0.0.1':
            return True    
    
        for block in self.hook_blocks:
            if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
                return True
        return False

