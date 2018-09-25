import yaml
import logging
import dateutil.parser
from gnome.policies import Policy
from gnome.gh import Repo


logger = logging.getLogger(__file__)

class PropagateMilestones(Policy):
    """ A policy to propagate upstream milestones to downstream repos

    This policy receives events for upstream

    """
    def dispatch_gnome(self):
        headers = self.callback.headers()
        event = headers['X-GitHub-Event']

        if event not in ('milestone'):
            return

        payload = self.callback.payload()
        action = payload['action']

        # TODO: refactor this into a config manager that better handles
        #       plugin-specific config
        config = self.config.get_yaml()
        config = config.get('propagate_milestones')

        # Slave list
        slaves = config.get('slaves', None)

        if not slaves:
            logger.info('No slaves were detected in config')
            return

        milestone = payload['milestone']
        title = milestone['title']
        due_on = milestone.get('due_on', None)
        due_on = dateutil.parser.parse(due_on) if due_on else None


        if action in ('created', 'opened', 'edited'):
            for slave in slaves:
                repo = Repo(slave)
                repo.upsert_milestone(
                    title,
                    state=milestone.get('state', None),
                    description=milestone.get('description', None),
                    due_on=due_on
                )

        if action in ('closed', 'deleted'):
            # Try to get the milestone first
            for slave in slaves:
                repo = Repo(slave)
                milestone =  repo.milestones.get(title)
                if milestone:
                    milestone._milestone.edit(title, state='closed')
