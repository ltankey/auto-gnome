import sys
import json
from zappa.async import task
from . import Policy

class VerboseCallbackLogging(Policy):
    """
    Verbose Callback Logging
    ========================

    This policy is very simple, it is primarially used for debugging
    the ticket gnome itself.

    As a Gnome user, enabling this policy will achieve nothing because
    you don't have access to the logs it creates.

    As a Gnome operator, you may find it useful for debugging but
    probably not.

    As a Gnome developer, it serves as a canonical example of how to
    create a policy to be enacted by the Gnome. That is why there is
    so much more documentation than code.
    """
    @task
    def dispatch_gnome(self):
        """
        You can consider the "dispatch_gnome" method like "main" method
        for gnomes. It is the only method every subclass of Policy requires,
        and is the method invoked in response to callback event from GitHub
        (if the repo is configured with this policy active).

        Note: the (optional) use of the zappa.async.task decorator. This
        nifty gadget dispatches this gnome asynchronously in it's own lambda
        process (returns instantly), effectively making this method a
        procedure rather than a function. If not deployed in lambda, the
        decorator should do nothing (run synchronously in the usual way).
        """
        print("verbose callback logging enabled", file=sys.stdout)
        # the inherited constructor creates self.callback
        callback_payload = self.callback.payload()
        # all this policy does is log the callback payload to stdout
        print(json.dumps(callback_payload, sort_keys=True, indent=4), 
              file=sys.stdout)

