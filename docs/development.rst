Development
===========

There are two topics really, policies and the gnome itself.

By the way, all the code is in GitHub (duh) https://github.com/bugflow/gh-ticket-gnome


Hacking the gnome itself
------------------------

See `src/app.py` for the very basic flask app. It's job is to receive callback from GitHub and process them.

.. automodule:: app
   :members:
   :undoc-members:

The flask app process callbacks with code if gets from `src/utils.py`. The result of it's callback processing is to call the `dispatch_gnome()` method on every policy that is configured for the repo (that the was the source of the callback event).

.. automodule:: util
   :members:
   :undoc-members:
      

TODO: when we have a `tests.py`, automodule that too.


Hacking Policies
----------------

Assuming everything is working, you probably want to hack on "policies". They are the things that do the stuff you want done. They are kind of like plugins. Users specify the policy they want to operate in their repo (using .gnome.yml), and you write the policy in python code that does what they want. Whenever the service get's a callback from GitHub, it "dispatches" all the configured policies. Simple.

TODO: cog-out documentation for all the policies
