import sys
import json
from policies import Policy

class SortingHat(Policy):
    def dispatch_gnome(self):
        print("sorting hat policy enabled", file=sys.stdout)
        """
        ensure the "sorting_hat" milestone exists
        ensure the sorting_hat milestone has no due date
        if the event was a new ticket:
            if the new ticket has no milestone, put it in the sorting hat
        if the event was a changed ticket:
            if the changed ticket has no milestone, put it in the sorting hat
        """
        pl = self.callback.payload()
        js = json.dumps(pl, sort_keys=True, indent=4) 
