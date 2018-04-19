import requests
import ipaddress
import yaml
import base64
import json
from github import Github
from datetime import datetime

import config

GITHUB_USER = config.GITHUB_USER
GITHUB_PSX = config.GITHUB_PSX

gh = Github(GITHUB_USER, GITHUB_PSX)

def repo_from_callback(callback):
    full_name = callback.payload()['repository']['full_name']
    return Repo(full_name)

class ProjectsMixin:
    ACCEPT_HEADER = 'application/vnd.github.inertia-preview+json'
    @property
    def projects(self):
        if not self._projects:
            r = requests.get(
                f'https://api.github.com/{self.api_path}/projects',
                auth=(GITHUB_USER, GITHUB_PSX),
                headers={'Accept': ProjectsMixin.ACCEPT_HEADER}
            )

            if r.status_code == 200:
                self._projects = [Project(p) for p in r.json()]
            else:
                raise Exception(f"Couldn't access project board list for  {self.name}")
        return self._projects

    def create_project(self, name, body):
        r = requests.post(
            f'https://api.github.com/{self.api_path}/projects',
            auth=(GITHUB_USER, GITHUB_PSX),
            headers={'Accept': ProjectsMixin.ACCEPT_HEADER},
            data=json.dumps({'name': name, 'body': body})
        )

        if r.status_code == 201:
            return Project(json.loads(r.text))
        raise Exception(f"Couldn't create a project! {r}")

    def has_project(self, name):
        return name in [p.name for p in self.projects]

    def get_project(self, name):
        for project in self.projects:
            if project.name == name:
                return project
        return None


class Organization(ProjectsMixin):
    def __init__(self, name):
        self.name = name
        self._projects = []
        self.api_path = f'orgs/{name}'
        # self.

class Project:
    def __init__(self, data):
        self._data = data
        self._columns = []
        self.name = data['name']
        self.state = data['state']

    def update(self, state):
        r = requests.patch(
            self._data['url'],
            auth=(GITHUB_USER, GITHUB_PSX),
            headers={'Accept': ProjectsMixin.ACCEPT_HEADER},
            data=json.dumps({'state': state})
        )
        if r.status_code == 200:
            return True
        raise Exception("Couldn't update project")

    def fetch_columns(self):
        r = requests.get(
            f'{self._data["url"]}/columns',
            auth=(GITHUB_USER, GITHUB_PSX),
            headers={'Accept': ProjectsMixin.ACCEPT_HEADER},
        )

        if r.status_code = 200:
            self._columns = json.dumps(r.text)
        else:
            raise Exception("Couldn't access project columns")

    @property
    def columns(self):
        if not self._columns:
            self.fetch_columns()
        return self._columns

    def has_column(self, column_name):
        return column_name in [c['name'] for c in self.columns]

    def get_column(self, column_name):
        for column in self.columns:
            if column['name'] == column_name:
                return column
        return None

    def add_ticket(column_name, issue_id):
        column = self.get_column(column_name)
        if not column:
            raise Exception("No such column by that name")

        r = requests.post(
            f'{column["url"]}/cards',
            auth=(GITHUB_USER, GITHUB_PSX),
            headers={'Accept': ProjectsMixin.ACCEPT_HEADER},
            data=json.dumps({'content_id': issue_id, 'content_type': 'Issue'})
        )

    def create_column(self, column_name):
        r = requests.post(
            f'{self._data["url"]}/columns',
            auth=(GITHUB_USER, GITHUB_PSX),
            headers={'Accept': ProjectsMixin.ACCEPT_HEADER},
            data=json.dumps({'name': column_name})
        )
        if r.status_code == 200:
            self.fetch_columns()
            return True

        raise Exception("Couldn't create a project column")

class Column:
    def __init__(self, data):
        self._data = data
        self.name = data['name']


class Milestone:
    """
    Wrapper of pygithub.Milestone.Milestone with cache and
    convenience methods. Bound to a Repo instance for
    access to the Github connection (credentials etc).
    """
    def __init__(self, repo, milestone):
        # FIXME: ensure repo is instance of Repo, and milestone
        # is instance of pygithub.Milestone.Milestone
        # Could eventually inherit it?
        self.repo = repo
        self._milestone = milestone

    @property
    def due_on(self):
        # return the due date of the milestone
        return self._milestone.due_on

    @property
    def description(self):
        return self._milestone.description

    @property
    def title(self):
        return self._milestone.title

    @property
    def number(self):
        return self._milestone.number

    @property
    def state(self):
        return self._milestone.state

    def open_tickets(self):
        # TODO: might be nice to rename this to open_issues for consistency
        repo_tickets = self.repo._repo.get_issues(
                milestone=self._milestone)
        return [Issue(self.repo, i) for i in repo_tickets]

    def update(self, **kwargs):
        """ Proxy method for underlying _milestone """

        # TODO: can probably replace this if we inherit from github.Milestone
        self._milestone.edit(self.title, **kwargs)


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


class Repo(ProjectsMixin):
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
        self._repo = gh.get_repo(repo_name)
        self._milestones = None # lazy
        self.api_path = f'repos/{repo_name}'

    def fetch_milestones(self):
        """ Refresh the milestone list from the Github API """
        self._milestones = {
            x.title: Milestone(self, x) for x in self._repo.get_milestones(state='all')
        }

    def get_last_active_milestone(self, prefix=''):
        """ Return the milestone with the most recent due_on value """
        milestones = sorted(
            [x for x in self.milestones.values() if x.due_on and x.title.startswith(prefix)],
            key=lambda x: x.due_on
        )

        expired_milestones = [
            x for x in milestones if datetime.date(x.due_on) < datetime.date(datetime.today())
        ]
        return expired_milestones[-1] if expired_milestones else None

    def get_active_milestone(self, prefix=''):
        """ Return the milestone with a future due_on value closest to today """
        milestones = sorted(
            [x for x in self.milestones.values() if x.due_on and x.title.startswith(prefix)],
            key=lambda x: x.due_on
        )

        unexpired_milestones = [
            x for x in milestones if datetime.date(x.due_on) > datetime.date(datetime.today())
        ]
        return unexpired_milestones[0] if unexpired_milestones else None

    @property
    def organization_name(self):
        return self._repo.organization.login

    @property
    def milestones(self):
        if not self._milestones:
            self.fetch_milestones()
        return self._milestones

    def upsert_milestone(self, title, **kwargs):
        milestone = self.milestones.get(title, None)

        if milestone:
            milestone.update(**kwargs)
        else:
            self.create_milestone(title, **kwargs)

    def get_config(self):
        conf_file = self._repo.get_contents('.bugflow/.gnome.yml')
        if conf_file:
            return yaml.load(base64.b64decode(conf_file.content))


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
        return milestone_name in self.milestones


    def get_milestone(self, milestone_name, cache=True):
        """
        Returns the milestone with by name (or None)
        """
        if not cache:
            self.fetch_milestones()

        return self.milestones.get(milestone_name, None)


    def create_milestone(self, milestone_name, state='open', description=None, due_on=None):
        """
        If the milestone does not exist, create it.

        If (optional) date passed in, set that date on the
        milestone. Dito for description. Otherwise, both empty.

        Returns the created (or pre-existing) Milestone instance.
        """
        # cast strings to unicode
        description = f'{description or ""}'
        milestone_name = u"{}".format(milestone_name)

        if self.milestone_exists(milestone_name):
            # FIXME: should we raise an error here, or just log?
            # FIXME: what to do if dates differ, upsert?
            return self.get_milestone(milestone_name)

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

            self._repo.create_milestone(
                milestone_name,
                state=state,
                description=description,
                due_on=due_on)
        else:
            self._repo.create_milestone(
                milestone_name,
                state=state,
                description=description)

        return self.get_milestone(milestone_name, cache=False)


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

