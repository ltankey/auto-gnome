import logging
from config import SCHEDULED_REPO_NAMES
from gh import Repo, Organization
from policies import Policy
from util import Config
import pdb

logger = logging.getLogger(__file__)

class AutoSprint:
    """ A schedule to automatically created GitHub projects

    This is a timed policy running on some configured interval, which
    checks to see whether there is a new "active" milestone, and if so,
    does some cleanup of tickets on the old "active" milestone, and
    creates a new GitHub project board for the new milestone.
    """

    def close_previous_sprint(self, location, milestone):
        pass

    def open_new_sprint(self, location, milestone):
        pass

    def get_kanban_location(self, repo, location):
        if location == 'org':
            return Organization(repo.organization_name)
        else:
            return repo

    def get_sorting_hat_milestone(self, repo):
        if not 'sorting hat' in [x.title for x in repo.milestones]:
            return repo.create_milestone('sorting hat')
        return repo.get_milestone('sorting hat')

    def dnf_label_exists(self, repo):
        return 'did not finish' in [x.name for x in repo._repo.get_labels()]

    def create_and_setup_project(self, target, name, milestone):
        # Create project
        project = target.create_project(name, name)

        # Create columns
        columns = ['backlog', 'in progress', 'blocked', 'QA']
        for column in columns:
            project.create_column(column)

        # Add tickets
        backlog = project.get_column('backlog')




    def run(self):
        # Get some list of repositories to check
        # TODO: sort out persistence
        pdb.set_trace()
        repo_names = [x.strip() for x in SCHEDULED_REPO_NAMES.split(',')]
        for repo_name in repo_names:
            # FIXME: This would probably be better accessed through repo.config
            # as config logically should be returned by accessing a repo.
            # This is a bit much...
            config = Config(repo_name=repo_name).get_yaml().get('auto_sprint')
            location = config.get('location')

            repo = Repo(repo_name)
            target = self.get_kanban_location(repo, location)

            last_active_milestone = repo.get_last_active_milestone()
            active_milestone = repo.get_active_milestone()

            # Close the most recent milestone
            if last_active_milestone and last_active_milestone.state == 'open':
                last_active_milestone.update(state='closed')

                # Create sorting hat milestone if it doesn't exist
                sorting_hat = self.get_sorting_hat_milestone(repo)

                # Create the did not finish label if it doesn't exist
                # TODO: label config should be defined somewhere nice
                if not self.dnf_label_exists(repo):
                    repo._repo.create_label(
                        'did not finish',
                        'd3d3d3'
                    )

                remaining_issues = last_active_milestone.open_tickets()

                # Apply the label
                for issue in remaining_issues:
                    issue._issue.add_to_labels('did not finish')

                # Move the issues to the sorting hat milestone
                for issue in remaining_issues:
                    issue._issue.edit(
                        milestone=sorting_hat._milestone
                    )

                # Close our old kanban if it exists
                project = target.get_project(last_active_milestone.title)
                if project:
                    project.update('closed')

            if active_milestone:
                # Upsert project board for active_milestone
                project = target.get_project(active_milestone)
                if not project:
                    self.create_and_setup_project(target, name, milestone)
                # if project:
                #     if project.state == 'closed':
                #         project.update('open')
                # else:
                #     project = target.create_project(active_milestone.title, active_milestone.title)

                # Initialize project columns
                # project.setup()

            # if active_milestone:
            #     if not active_milestone.title in [x.name for x in target.projects]:
            #         # Need to open a new kanban board