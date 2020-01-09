.. _installation:

Installation of the Simulator
=============================

The Simulator is written in `Python`_ version 3,
and requires a number of python modules
which must be installed prior to using the Simulator.
We recommend `Using Docker`_ because this eliminates build problems
and greatly simplifies user support through everyone sharing
the same environment.
The alternative is to do a `Manual Installation`_.

.. _Python: https://www.python.org

We recommend *not* using the pipeline in the same environment as the Simulator,
as the presence of the large Simulator package, drp_instdata,in the environment
causes long delays when the pipeline checks the versions of packages.
Use a separate terminal (or ``screen``) for maximum efficiency.


Using Docker
------------

If you are not familiar with Docker,
read the "Installation / Using Docker" section of
the 2D DRP Pipeline User Documentation for an introduction.

To run a Docker image containing the Simulator, run::

    docker run -ti paprice/pfs_sim2d:latest

You'll probably want to include some ``-v <machineDir>:<containerDir>``
arguments to map some directories from your machine to the Docker container,
if only to persist files created by the simulator.

Be sure to ``setup drp_instmodel`` to configure the environment.


Manual Installation
-------------------

The Simulator requires the LSST stack
(at least up to and including the afw package),
the `fitsio`_ python module (which is not provided in the LSST stack),
and the datamodel, drp_instdata and drp_instmodel PFS packages.

.. _fitsio: https://pypi.org/project/fitsio/

We recommend you install and ``setup`` the PFS 2D DRP software,
(which includes the LSST stack and the datamodel PFS package),
and then install fitsio and the remaining PFS packages.

You can check for the existence of the fitsio python module with
the following shell command::

    python3 -c '
    try:
        import fitsio
    except ImportError as exc:
        print("Unable to import fitsio: %s" % (exc,))
    else:
        print("fitsio OK")
    '

If that command reveals that it is missing,
you can install them with ``pip3`` [#]_::

    pip3 install fitsio

.. [#] ``pip3`` might simply be named ``pip`` on your system;
       we use ``pip3`` here to emphasise that this is the ``pip``
       that goes with python 3.

Once the dependencies have been installed,
clone the necessary PFS packages::

    git clone git://github.com/Subaru-PFS/drp_instdata
    git clone git://github.com/Subaru-PFS/drp_instmodel

Note that drp_instdata is a large |git-lfs|_ package,
and can take a while to download.

.. |git-lfs| replace:: ``git-lfs``
.. _git-lfs: https://git-lfs.github.com

Then declare each of the the two PFS packages::

    eups declare drp_instdata git -t current -r /path/to/drp_instdata
    eups declare drp_instmodel git -t current -r /path/to/drp_instmodel

Each time you use the simulator, you'll need to ``setup drp_instmodel``
and ``setup drp_instdata``.
