Development
===========

There are two topics really, policies and the gnome itself.

By the way, all the code is in GitHub (duh) https://github.com/bugflow/auto-gnome


Hacking the gnome itself
------------------------

.. graphviz::

   digraph d {
      node[shape=rectangle]

      subgraph cluster_codebase {
         label="codebase";
	 app [label="app.py\n(process callbacks)"];
	 util [label="util.py\n(abstraction)"];
	 policy [label="policies/__init__.py\n(register plugins)"];
	 plugins [label="plugins/*\n(do interesting things)"];
         app -> util -> policy -> plugins;
      }
      GitHub
      callback [shape=ellipse]
      ghapi [shape=ellipse label="GitHub\nAPI v3"]
      callback -> GitHub [dir=back]
      app -> callback [dir=back];
      util -> ghapi;
      GitHub -> ghapi [dir=back];
      anything [shape=ellipse];
      plugins [shape="folder"];
      plugins -> anything;
      plugins -> ghapi;
      humans -> GitHub;
   }


src/app.py
^^^^^^^^^^

See `src/app.py` for the very basic flask app. It's job is to receive callback from GitHub and process them.

.. automodule:: app
   :members:
   :undoc-members:


src/utils.py
^^^^^^^^^^^^

The flask app process callbacks with code if gets from `src/utils.py`. The result of it's callback processing is to call the `dispatch_gnome()` method on every policy that is configured for the repo (that the was the source of the callback event).

.. automodule:: util
   :members:
   :undoc-members:


src/tests.py
^^^^^^^^^^^^

TODO: when we have a `tests.py`, automodule that too.


src/policies/__init__.py
^^^^^^^^^^^^^^^^^^^^^^^^

The util module instantiates the `policy` module. This is a very simple thing, all it does is import the relevant classes (from modules in the plugins directory).

When you make a new plugin, it won't do anything until you register it by importing the relevant class into policies/__int__.py

Browse from there the plugins (see next section, Hacking Policies)...


Hacking Policies
----------------

Assuming everything is working, you probably want to hack on "policies". They are the things that do the stuff you want done. They are kind of like plugins. Users specify the policy they want to operate in their repo (using .gnome.yml), and you write the policy in python code that does what they want. Whenever the service get's a callback from GitHub, it "dispatches" all the configured policies. Simple.

.. [[[cog
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
