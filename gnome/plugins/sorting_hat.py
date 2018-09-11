import sys
import os.path
import json

from gnome.gh import (Milestone, Issue, Repo)
from gnome.policies import Policy

# TODO: this should optionally come from config in .gnome.yml
SORTING_HAT_MILESTONE = "The Sorting Hat"


class SortingHat(Policy):
    """
    The "Sorting Hat" is a milestone with no due-date, that signifies
    some sort of ticket grooming/prioritisation process is necessary.

    The sorting hat is like an in-tray for the person/people responsible
    for assessing and prioritising tickets.

    .. code:: gherkin

       As a software developer
       I want my auto-gnome to use a sorting hat policy
       So that my tickets are continuously groomed and prioritised

    """
    def dispatch_gnome(self):
        # we only care about issues and milestones
        headers = self.callback.headers()
        event = headers['X-GitHub-Event']
        if event not in ('issue', 'milestone'):
            return

        payload = self.callback.payload()
        action = payload['action']

        if event == 'issue':
            if action in ('created', 'demilestoned'):
                # we only care about new issues
                # or issues that lost their milestones

                repo = repo_from_event(self.callback)
                gh_issue = repo.get_issue(payload['issue'])
                issue = Issue(repo, gh_issue)

                if action == 'created':
                    if not issue.has_milestone():
                        repo.ensure_milestone_exists(
                            SORTING_HAT_MILESTONE)
                        repo.ensure_milestone_has_due_date(
                            SORTING_HAT_MILESTONE, None)
                        issue.move_to_milestone(
                            SORTING_HAT_MILESTONE)
                elif action == 'demilestoned':
                    if issue.is_open():
                        repo.ensure_milestone_exists(
                            SORTING_HAT_MILESTONE)
                        repo.sensure_milestone_has_due_date(
                            SORTING_HAT_MILESTONE, None)
                        issue.move_to_milestone(
                            SORTING_HAT_MILESTONE)

        elif event == 'milestone':
            if action == 'closed':
                # we only care about milestones as they close

                repo = repo_from_event(self.callback)
                gh_milestone = repo.get_milestone(payload[''])
                milestone = Milestone(repo, gh_milestone)

                repo.ensure_milestone_exists(
                    SORTING_HAT_MILESTONE)
                repo.sensure_milestone_has_due_date(
                    SORTING_HAT_MILESTONE, None)

                for issue in milestone.get_open_tickets():
                    issue.move_to_milestone(
                        SORTING_HAT_MILESTONE)


def repo_from_event(callback):
    # TODO: figure out the Repo constructor paramaters
    return Repo()
