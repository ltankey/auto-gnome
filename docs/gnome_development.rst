Hacking the gnome itself
========================


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


Codebase
--------

The callback service is provided by a Flask app, and the code for this is in `gnome/app.py`. It's only job is to receive callbacks from GitHub and process them.

app.py delegates the interesting stuff to code in `gnome/utils.py`. This does two things, interacts with GitHub to obtain configuration, then delegates configured tasks to the plugins (via the plugin register, `gnome/policies/__init__.py`)

Ultimately, interesting stuff is delegated to plugins. All plugins must provide a `dispatch_gnome()` method. If configured, this is called with data from the originating callback event (and config).



app.py
^^^^^^

.. automodule:: gnome.app
   :members:
   :undoc-members:


gnome/utils.py
^^^^^^^^^^^^

.. automodule:: util
   :members:
   :undoc-members:


gnome/gh.py
^^^^^^^^^

.. automodule:: gh
   :members:
   :undoc-members:


gnome/policies/__init__.py
^^^^^^^^^^^^^^^^^^^^^^^^

The util module instantiates the `policy` module. This is a very simple thing, all it does is import the relevant classes (from modules in the plugins directory).

When you make a new plugin, it won't do anything until you register it by importing the relevant class into policies/__int__.py

Browse from there the plugins (see next section, Hacking Policies)...


Tests
-----

.. automodule:: tests.test_gh
   :members:
   :undoc-members:

.. automodule:: tests.test_config
   :members:
   :undoc-members:

.. automodule:: tests.test_callback
   :members:
   :undoc-members:
