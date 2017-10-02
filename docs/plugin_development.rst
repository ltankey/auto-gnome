Plugin Development
==================

Assuming everything is working, you probably want to hack on "policies". They are the things that do the stuff you want done. They are kind of like plugins. Users specify the policy they want to operate in their repo (using .gnome.yml), and you write the policy in python code that does what they want. Whenever the service get's a callback from GitHub, it "dispatches" all the configured policies. Simple.

.. [[[cog
.. # FIXME: move this into a cog.py so rst has a simple one-liner.
.. import re
.. import policies
.. ignore_pattern = re.compile("^__.+__$")
.. ignore_list = ("sys")
.. for x in dir(policies):
..     if not ignore_pattern.match(x) and x not in ignore_list:
..         cog.outl("")
..         cog.outl(x)
..         underline = "^"*len(x)
..         cog.outl(underline)
..         cog.outl("")
..         cog.outl(".. autoclass:: policies.{}".format(x))
..         cog.outl("   :members:")
..         cog.outl("   :undoc-members:")
..         cog.outl("")
.. ]]]

Policy
^^^^^^

.. autoclass:: policies.Policy
   :members:
   :undoc-members:


SortingHat
^^^^^^^^^^

.. autoclass:: policies.SortingHat
   :members:
   :undoc-members:


VerboseCallbackLogging
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: policies.VerboseCallbackLogging
   :members:
   :undoc-members:

.. [[[end]]]
