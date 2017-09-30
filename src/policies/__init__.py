import sys

class Policy(object):
    def __init__(self, callback):
        self.callback=callback

    # this should probably accept arbitrary kw arguments
    def dispatch_gnome(self):
        """ The method that does the stuff you want done
        
        This method must be over-ridden in actual policies
        """
        class AbstractBaseGnomePolicyCanNotBeDispatchedError(Exception): pass
        raise AbstractBaseGnomePolicyCanNotBeDispatchedError()


# this is where policies are registered
from .verbose_callback_logging import VerboseCallbackLogging
from .sorting_hat import SortingHat
