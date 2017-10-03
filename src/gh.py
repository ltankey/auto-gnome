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
    Wrapper of pygithub.Milestone.Milestone with cache and
    convenience methods. Bound to a Repo instance for 
    access to the Github connection (credentials etc). 
    """
    def __init__(self, repo, milestone):
        # FIXME: ensure repo is instance of Repo, and milestone
        # is instance of pygithub.Milestone.Milestone
        self.repo = repo
        self._milestone = milestone

    def get_date(self):
        # return the due date of the milestone
        return self._milestone['due_on']

    def get_description(self):
        return self._milestone['description']

    def get_name(self):
        return self._milestone['title']

    def open_tickets(self):
        found = []
        for i in self.repo._repo.get_issues(
                milestone=self._milestone):
            found.append(Issue(self.repo, i))
        return found

    
class Issue:
    """
    Wrapper of pygithub.Issue.Issue, with cache and convenience
    methods.
    """
    def __init__(self, repo, gh_issue):
        self.repo = repo
        self._issue = gh_issue

    def has_milestone(self):
        milestone = self._issue.milestone
        if milestone:
            return True
        return False

    def move_to_milestone(self, new_milestone):
        if not self.repo.milestone_exists(new_milestone):
            self.repo.create_milestone(new_milestone)
        m = self.repo.get_milestone(new_milestone)
        self._issue.milestone = m._milestone


class Repo:
    """
    This class is an abstraction over the GitHub repository.

    It interacts with GitHub as the configured user. Note this
    is a double-stacked abstraction (it's a wrapper around the
    PyGithub library, which wraps the GitHub API v3). That makes
    the code seem a little strange on first reading, however it
    simplifies mocking in tests at the business logic layer.
    """
    def __init__(self, repo_name):
        self.name = repo_name
        gh = Github(GITHUB_USER, GITHUB_PSX)
        self._repo = gh.get_repo(repo_name)
        self._milestones = None # lazy

    def ensure_milestone_exists(self, milestone_name,
                                description=None, date=None):
        """
        If the repo does not have a milestone with the given name
        then create one.

        If description or date parameters are provided, and the
        milestone is created, then they will be used.

        If the milestone already exists, and the date or description
        differ from the ones provided, they will be ignored. This
        is NOT follow the "upsert" pattern.
        """
        if not self.milestone_exists(milestone_name):
            self.create_milestone(milestone_name,
                                  description=description,
                                  date=date)

    def ensure_milestone_has_due_date(self, milestone_name, due_date):
        """
        If the milestone does not have a due date, or if it has
        a due date that differs from the one provided, then
        update the due date to the one provided.
        """
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

    def create_milestone(self, milestone_name, description=None, due_on=None):
        """
        If the milestone does not exist, create it.

        If (optional) date passed in, set that date on the
        milestone. Dito for description. Otherwise, both empty.

        Returns the created (or pre-existing) Milestone instance.
        """
        # cast strings to unicode
        description = u"{}".format(milestone_name)
        milestone_name = u"{}".format(milestone_name)

        #always
        STATE = u"open"

        if self.milestone_exists(milestone_name):
            # FIXME: should we raise an error here, or just log?
            # FIXME: what to do if dates differ, upsert?
            return self.get_milestone(milestone_name)
        # cast None description to empty strings
        if not description:
            description = u''
        # accept due_on as string or datetime.date
        if due_on:
            import datetime  # when working, move to head
            if type(due_on) == type(str("")):
                #try:
                due_on = datetime.date.fromtimestamp(due_on)
                raise Exception(due_on)  # DEBUG
                #except:
                #    # FIXME: what to do if due_on can not be recast?
                #    pass  # probably not that, custom exception?
            elif type(due_on) == type(datetime.date(2017, 10, 10)):
                pass

            self._repo.create_milestone(
                milestone_name,
                state=STATE,
                description=description,
                due_on=due_on)
        else:
            self._repo.create_milestone(
                milestone_name,
                state=STATE,
                description=description)

        return self.get_milestone(milestone_name)


class EventSourceValidator:
    """
    GitHub publishes the address ranges that they make callbacks from.
        
    Instances of this class can be used to validate ip addresses,
    like a kind of dymanic whitelist.
    """
    def __init__(self):
        self.hook_blocks = None

    def get_hook_blocks(self):
        """
        Fetch the whitelisted addresses blocks published by
        GitHub (directly, or from cache).
        """
        # FIXME: use network cache service (redis, memcache, etc)
        # TODO: evaluate use of classmethod cache (singleton pattern)?
        if self.hook_blocks:
            return self.hook_blocks
        hb = requests.get('https://api.github.com/meta').json()['hooks']
        self.hook_blocks = hb
        return hb

    def ip_str_is_valid(self, ip_str):
        """
        This function returns true if the IP address (string) passed to it
        is within the address blocks published by GitHub.
        """
        request_ip = ipaddress.ip_address(u'{0}'.format(ip_str))
        if str(request_ip) == '127.0.0.1':
            return True    
    
        for block in self.get_hook_blocks():
            if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
                return True
        return False

