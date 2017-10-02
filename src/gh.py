import requests
import ipaddress
from github import Github


# TODO: this should definitely be coming from the environment
import local_secrets
GITHUB_USER = local_secrets.GITHUB_USER
GITHUB_PSX = local_secrets.GITHUB_PSX

def repo_from_callback(callback):
    full_name = callback.payload()['repository']['full_name']
    return Repo(full_name)


class Milestone:
    """
    Wrapper of pygithub.Milestone.Milestone
    with cache and convenience methods.
    """
    def __init__(self, repo, milestone):
        self._repo = repo
        self._milestone = milestone

    def open_tickets(self):
        return ()

    
class Issue:
    def has_milestone(self):
        return True
    def move_to_milestone(self, new_milestone):
        pass


class Repo:
    def __init__(self, repo_name):
        self.name = repo_name
        gh = Github(GITHUB_USER, GITHUB_PSX)
        self._repo = gh.get_repo(repo_name)
        self._milestones = None # lazy

    def ensure_milestone_exists(self, milestone_name, date=None):
        if not self.milestone_exists(milestone_name):
            self.create_milestone(milestone_name, date=date)

    def ensure_milestone_has_due_date(self, milestone_name, due_date):
        milestone = self.get_milestone(milestone_name)
        found_due_date = milestone.get_due_date()
        # FIXME: use propper date comparisons (not strings)
        if found_due_date != due_date:
            milestone.set_due_date(due_date)

    def milestone_exists(self, milestone_name):
        """
        Returns True if the milestone exists.
        """
        if not self._milestones:
            self._milestones = []
            for _milestone in self._repo.get_milestones(state="all"):
                m = Milestone(self._repo, _milestone)
                self._milestones.append(m)
        found = False
        for m in self._milestones:
            if m._milestone.title == milestone_name:
                found = True
        return found

    def get_milestone(self, milestone_name):
        """
        Returns the milestone with the name (or None)
        """
        # force lazy evaluation
        if self.milestone_exists(milestone_name):
            for m in self._milestones:
                if m._milestone.title == milestone_name:
                    return m
        return None

    def create_milestone(self, milestone_name, date=None):
        """
        If the milestone does not exist, create it.

        If (optional) date passed in, set that date on the
        milestone.
        """
        # FIXME: validate date input (if not None)
        # accept strings of dates?
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

