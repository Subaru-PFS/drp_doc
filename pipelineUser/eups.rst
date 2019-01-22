.. _eups:

EUPS
====

EUPS stands for "Extended [#]_ Unix Products System".
It is a system for managing software products with multiple versions,
along with their dependencies.
The great strength of EUPS compared to a regular system package manager
(like `Homebrew`_ or `yum`_)
is that it allows different versions of software products to be used,
so you can substitute one version for another [#]_ without the need to recompile
(it is similar to the |module|_ command commonly used on clusters).
It works by configuring certain environment variables that Unix-ish systems recognise,
including ``PATH`` and ``LD_LIBRARY_PATH`` [#]_.
The code is available `on GitHub`_.

EUPS has a great many features, but many are not relevant for simply using the PFS 2D DRP.
Here we introduce a few useful commands that will allow you to operate EUPS for use with the pipeline.

.. [#] Or "Evil", depending on who you ask.
.. _Homebrew: https://brew.sh
.. _yum: http://yum.baseurl.org
.. |module| replace:: ``module``
.. _module: http://modules.sourceforge.net
.. [#] Modulo concerns about ABI compatibility.
.. [#] ``DYLD_LIBRARY_PATH`` on OSX; and to work around `SIP`_, ``LSST_LIBRARY_PATH`` as well.
.. _SIP: https://en.wikipedia.org/wiki/System_Integrity_Protection
.. _on GitHub: https://github.com/RobertLuptonTheGood/eups


setup
-----

``setup`` is the main interface of EUPS.
It loads a particular version of a particular package
(and, by default, its dependencies) into the environment.
For example::

    setup pfs_pipe2d

will load the ``pfs_pipe2d`` product tagged ``current``,
and its dependencies.

To load a particular version (and its dependencies),
simply specify the version along with the product::

    setup pfs_pipe2d 5.0

To use the definition of the ``pfs_pipe2d`` that you have locally
(e.g., cloned from GitHub and being edited)
but not modify any dependencies that have already been loaded::

    setup -j -r /path/to/pfs_pipe2d

Here, the ``-j`` flag means to load *just* this package (i.e., no dependencies).
Its cousin, the ``-k`` flag means to load dependencies,
but *keep* the version of any dependency that has already been loaded.


unsetup
-------

``unsetup`` is the opposite of ``setup``:
it removes a particular package (and, by default, its dependencies) from the environment.
The ``-j`` flag means the same as for ``setup`` (i.e., don't ``unsetup`` the dependencies),
and is often useful.


eups list
---------

``eups list`` lists the available packages and versions,
along with tags applied to them.
If a particular package and version has been loaded, ``setup`` is among the tags.

For a list of packages that have been loaded, use::

    eups list -s

You can list the available versions of a particular package by specifying the package name,
e.g.,::

    eups list pfs_pipe2d

Or, to discover what version of a package you're using,
use the ``-s`` flag with the package name,
e.g.::

    eups list -s pfs_pipe2d


Tags
----

Packages can be tagged with a symbolic name
(e.g., the ticket name during development).
By default, the list of supported symbolic names is limited to ``current`` and the user name [#]_.
To expand the list of supported symbolic names,
you need to edit your ``~/.eups/startup.py`` file to include,
e.g.::

    hooks.config.Eups.userTags += ["myTag1", "myTag2"]

Then you can tag package versions::

    eups declare pfs_pipe2d 5.0 -t myTag1


.. [#] This limitation is deliberate, to prevent typos.
