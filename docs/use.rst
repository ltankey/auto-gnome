Using a Gnome
-------------

You do not need to install or run this code to use it.

All you need to do is:

 * create a .gnome.yml file in the root of your GitHub repository
 * configure the "policies" you want the gnome to follow
 * register the github web hook to the bugflow callback endpoint
 * give the gnome appropriate permissions to allow it to implement your policies


The .gnome.yml file
-------------------

The base directory of your hithub repo needs to have a file called .gnome.yml

TODO: insert screen shor of the bugflow repo, highlighting it's .gnome.yml

This needs to be a valid yaml file (TODO: link to the yaml web site)

The yaml file needs to contain a list of `policies`. The policies that are
available in this repository are the ones we find useful, you can develop
your own if you want to.

To ensure the GitHub Ticket Gnomes do the things you want them to do, the
first thing you have to do is tell them what those things are.

Here is an example of a very simple `.gnome.yml` file:

.. code-block:: yaml

   policies:
    - VerboseCallbackLogging
    - NonExistantPolicy
    - SortingHat


This tells the gnome to do three things:

 * Apply the VerboseCallbackLogging policy. This is a fairly silly thing for
   most users to do, because they can't see the logs that are produced. It
   may sometimes be usefull for DevOps crews working on the gnome itself.
   Basically, you are asking the gnome to mutter furiously to itself.
 * Apply the NonExistantPolicy. There is no such policy, so this will cause
   another kind of silent muttering (of no use to most users, and possible
   use to DevOps crews working on the gnome itself).
 * Apply the SortingHat policy. This is an example of something you might
   actually want to do. SortingHat policy is an example of a simple GitHub
   workflow automation.

Over time we might add more policies, including policies that you want to
use. Or you can develop your own. Either way, the `.gnome.yml` file is how
you tell your gnome what you want it to do in response to events in this
repository.


The Web Hook
------------

TODO:

 * write some words about wiring-up the GitHub web hook.
 * include a screenshot
 * resolve if we want to make an app integration or not?
 * resolve what to do about secrets / HMAC callback verification (etc)

At the moment, the gnome needs the user to manually configure a web hook in GitHub.

There may be bettwe ways to do this.


Available Policies
------------------

TODO: cog out the module docstring for each policy, with auto-generated headers
