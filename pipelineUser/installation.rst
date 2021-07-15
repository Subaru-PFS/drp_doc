.. _installation:

Installation
============

The PFS 2D DRP uses components from the `LSST Data Management stack`_.
We currently use LSST stack version ``18.1.0``,
so installing the PFS 2D DRP requires also installing this version of the LSST stack.
There are multiple ways of installing these.

#. `Using Docker`_ : use a pre-built Docker image containing both the LSST stack and the PFS 2D DRP modules.
#. `Install with a script`_ : use our script to both install the LSST stack and the PFS 2D DRP modules.
#. `Install manually from GitHub`_ : install the LSST stack and then the PFS 2D DRP modules.

.. _LSST Data Management stack: https://pipelines.lsst.io

For most work, we recommend `Using Docker`_,
as this provides the exact same environment we use in development,
thus completely eliminating installation problems;
however, this may not be possible in all cases,
and hence we provide the other installation mechanisms.
Before choosing one, we encourage you to read through each of these,
understanding the benefits and limitations of each.

No matter how you choose to install the software,
be sure to read the section on :ref:`eups`,
which gives instructions for loading the software into the environment.
After you've installed the software, try `Testing your installation`_.


Using Docker
------------

`Docker`_ allows you to run
a binary distribution in a pre-defined sandbox environment (an "image")
on your machine.
The great advantage of this is that this is the exact same image
produced and used by the development team,
which completely eliminates installation problems such as due to
missing dependencies,
incompatible dependencies,
or unexpected environments.
However, because the environment is carefully controlled,
you need to explicitly specify any use of your machine's physical characteristics.

.. _Docker: https://www.docker.com

The use of Docker is straightforward on a user-administered machine,
but since it runs as root,
admins of shared systems may be reluctant to allow use of Docker.
However, there are alternatives available which work around this problem,
including `Shifter`_ and `Singularity`_,
allowing the use of Docker images without root.

.. _Shifter: https://github.com/NERSC/shifter
.. _Singularity: https://singularity.lbl.gov

Your favourite package manager should already have a build of Docker,
so installation is simple, e.g.:

* Homebrew on Mac OSX: ``brew cask install docker``
* MacPorts on Mac OSX: ``sudo port install docker``
* Redhat/CentOS on Linux: ``sudo yum -y install docker``
* Ubuntu on Linux: ``sudo apt-get install docker``

The Docker web site has much more detailed information on `installing Docker`_.

.. _installing Docker: https://docs.docker.com/install/

With Docker installed,
you can download and start the image::

    docker run -ti paprice/pfs_pipe2d:latest

That runs the image in its own area (a "container"),
with none of your machine's resources
(e.g., disks, network)
shared.
If you want to access files on your machine (e.g., data to be reduced, or code to be used)
or persist anything you create beyond the lifetime of the container,
you will need to mount some directories
(with the argument ``-v localDir:containerDir``)
so they are accessible under Docker.
If you want to be able to display X windows from the container
(e.g., for matplotlib plots, or ds9),
additional arguments are required.
We recommend ``bash`` definitions like the following::

    pfsDocker () {
        docker run -ti -v ~/docker:/home/pfs -v ~/pfs:/home/pfs/pfs $DOCKER_OPTIONS --cap-add=SYS_PTRACE --security-opt seccomp=unconfined ${1-paprice/pfs_pipe2d:latest}
    }
    export DOCKER_OPTIONS="-e DISPLAY=docker.for.mac.localhost:0"  # For Mac OSX only

This mounts the ``~/docker`` directory on your machine to the container's home directory
(which allows for persistence of anything you do under the home directory,
including shell configuration files that make an environment comfortable),
and mounts the ``~/pfs`` directory on your machine to the same directory in the container
(useful for developing the code that you've put in that directory),
and allows network communication between your machine and the container
(you may have to do ``xhost +localhost`` on your machine to allow X windows from the container).
You can choose a different image by specifying it on the command-line;
e.g., the following runs an image that includes additional debugging facilities
(i.e., `gdb`_, `valgrind`_, `igprof`_ and a library required by ds9):

    pfsDocker paprice/pfs_pipe2d_debug:latest

.. _gdb: https://www.gnu.org/software/gdb/
.. _valgrind: http://valgrind.org
.. _igprof: https://igprof.org

Docker images are light on operating system features so as to minimize the size of the image.
If you find that you need an additional feature in the operating system
(e.g., a library or tool you want is missing),
you have two choices.
Firstly, the temporary solution is to log into the container as ``root`` and install what you want::

    docker exec -ti --user=root <containerId> /bin/bash

You can find the ``containerId`` from the ``hostname`` of the container,
or by running ``docker ps`` on your machine.
Note that this modifies the container (not the image),
so the effect will be lost when you exit the container.
For a more permanent solution,
you should build your own Docker image on top of the ``pfs_pipe2d`` image.
To do this, you need to write a |Dockerfile|_,
which is a prescription for generating the image;
then run::

    docker build -t <tagname> -f /path/to/Dockerfile

Here, ``<tagname>`` is a symbolic name for the image;
this is usually composed of a `DockerHub`_ username (e.g., ``paprice``),
a repository name (e.g., ``pfs_pipe2d``),
and a version tag (e.g., ``latest``)
all put together: ``<username>/<repositoryName>:<versionTag>``.
Once it's built, you can run your image in the same way as above.
For an example |Dockerfile|_ of an image layered on top of the ``pfs_pipe2d`` image,
see |Dockerfile.pipe2d_debug|_ and the accompanying |Makefile|_.

.. |Dockerfile| replace:: ``Dockerfile``
.. _Dockerfile: https://docs.docker.com/engine/reference/builder/
.. _DockerHub: https://hub.docker.com
.. |Dockerfile.pipe2d_debug| replace:: ``Dockerfile.pipe2d_debug``
.. _Dockerfile.pipe2d_debug: https://github.com/Subaru-PFS/pfs_pipe2d/blob/master/docker/Dockerfile.pipe2d_debug
.. |Makefile| replace:: ``Makefile``
.. _Makefile: https://github.com/Subaru-PFS/pfs_pipe2d/blob/master/docker/Makefile

If you're having problems in the container,
try `increasing the memory`_,
since Docker defaults to a mere 2GB of memory for its containers.
We regularly run with 4 cores and 8GB of memory,
which generally works fine.

.. _increasing the memory: https://stackoverflow.com/questions/44533319/how-to-assign-more-memory-to-docker-container


Install with a script
---------------------

We provide scripts for building and installing the LSST stack and the PFS 2D DRP software on your machine.
However, these require that several `Dependencies`_ are installed first,
and they may be fragile under idiosyncratic environments.
If you have problems with these scripts, see :ref:`help`
or try an alternative installation method [#]_.

.. [#] We recommend `Using Docker`_, as that completely eliminates build problems.

The scripts are:

* |install_lsst.sh|_: installs the LSST stack.
* |build_pfs.sh|_: builds the PFS 2D DRP software on top of an existing LSST stack installation.
* |install_pfs.sh|_: installs the LSST stack and builds the PFS 2D DRP software on top.

.. |install_lsst.sh| replace:: ``install_lsst.sh``
.. _install_lsst.sh: https://github.com/Subaru-PFS/pfs_pipe2d/blob/master/bin/install_lsst.sh
.. |build_pfs.sh| replace:: ``build_pfs.sh``
.. _build_pfs.sh: https://github.com/Subaru-PFS/pfs_pipe2d/blob/master/bin/build_pfs.sh
.. |install_pfs.sh| replace:: ``install_pfs.sh``
.. _install_pfs.sh: https://github.com/Subaru-PFS/pfs_pipe2d/blob/master/bin/install_pfs.sh

These scripts can be obtained either by downloading them directly from GitHub, e.g.::

    wget https://raw.githubusercontent.com/Subaru-PFS/pfs_pipe2d/master/bin/install_pfs.sh

or by cloning the entire `pfs_pipe2d`_ repository with ``git``
and then looking in the ``bin`` subdirectory::

    git clone http://github.com/Subaru-PFS/pfs_pipe2d
    cd pfs_pipe2d/bin

.. _pfs_pipe2d: https://github.com/Subaru-PFS/pfs_pipe2d


Dependencies
^^^^^^^^^^^^

The LSST stack, on which the PFS software is built,
requires the following Redhat/CentOS packages::

    install bison blas bzip2 bzip2-devel cmake curl flex fontconfig
    freetype-devel gawk gcc-c++ gcc-gfortran gettext git glib2-devel
    java-1.8.0-openjdk libcurl-devel libuuid-devel libXext libXrender
    libXt-devel make mesa-libGL ncurses-devel openssl-devel patch perl
    perl-ExtUtils-MakeMaker readline-devel sed tar which zlib-dev

If you're not running Redhat/CentOS,
check the list of `prerequisites for the LSST stack`_
and install the packages you need for your system.

.. _prerequisites for the LSST stack: https://pipelines.lsst.io/v/v18_1_0/install/newinstall.html#prerequisites

In addition to the above, |git-lfs|_ must be installed,
which involves installing both the binaries (usually through your system's package manager)
and the user configuration (``git lfs install``).
On Redhat/CentOS, this is a matter of::

    # Install the binaries
    sudo yum install -y epel-release
    sudo curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash
    sudo yum install -y git-lfs
    # Set up user configurations
    git lfs install

.. |git-lfs| replace:: ``git-lfs``
.. _git-lfs: https://git-lfs.github.com


Install LSST+PFS
^^^^^^^^^^^^^^^^

The last of the above-listed scripts, ``install_pfs.sh``, combines the first two;
it is the preferred choice for installing the software
if you do not have an existing installation of the LSST stack.
If you encounter a problem running this script,
try running the first two scripts in succession,
which will hopefully give more information on where the problem lies.
Running the script with the ``--help`` or ``-h`` command-line arguments gives the usage information::

    foo@bar:~/pfs/pfs_pipe2d/bin $ install_pfs.sh -h
    Install the PFS 2D pipeline.
    
    Usage: /home/foo/pfs/pfs_pipe2d/bin/install_pfs.sh [-b <BRANCH>] [-e] [-l] [-L <VERSION>] <PREFIX>
    
        -b <BRANCH> : name of branch on PFS to install
        -e : install bleeding-edge LSST
        -l : limited install (w/o drp_stella, pfs_pipe2d)
        -L <VERSION> : version of LSST to install
        -t : tag name to apply
        <PREFIX> : directory in which to install

``-e``, ``-l`` and ``-L``  are black-belt options:
do not use them unless you know what you are doing.
The ``-b`` option allows you to specify a particular version of the PFS pipeline to install
(e.g., a ticket branch, or an official release).
The ``-t`` option allows you to apply a :ref:`eups` tag (often ``current``).
An example usage, which will install the master branch under ``~/pfs/stack`` and tag it as ``current`` is::

    foo@bar:~/pfs/pfs_pipe2d/bin $ install_pfs.sh -t current ~/pfs/stack
    [...]
    All done.
    
    To use the PFS software, do:
    
        source /home/foo/pfs/stack/loadLSST.bash
        setup pfs_pipe2d -t current

Follow the instructions to configure your environment [#]_.

.. [#] The use of ``-t current`` in the ``setup`` command is not strictly necessary:
       ``eups`` defaults to looking for packages tagged ``current``.


Install PFS on existing LSST stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``build_pfs.sh`` script builds the PFS 2D DRP software
on top of an existing installation of the LSST stack.
It is useful if you have already used ``install_pfs.sh`` and want to upgrade the PFS software version,
or if you have independently installed the LSST stack
(perhaps with the ``install_lsst.sh`` script, or manually).

Running the script with the ``--help`` or ``-h`` command-line arguments gives the usage information::

    foo@bar:~/pfs/pfs_pipe2d/bin $ build_pfs.sh -h
    Install the PFS 2D pipeline.
    
    Requires that the LSST pipeline has already been installed and setup.
    
    Usage: /home/foo/pfs/pfs_pipe2d/bin/build_pfs.sh [-b <BRANCH>] [-l] [-t TAG]
    
        -b <BRANCH> : name of branch on PFS to install
        -l : limited install (w/o drp_stella, pfs_pipe2d)
        -t : tag name to apply

``-l`` is a black-belt option:
do not use it unless you know what you are doing.
The ``-b`` option allows you to specify a particular version of the PFS pipeline to install
(e.g., a ticket branch, or an official release).
The ``-t`` option allows you to apply a :ref:`eups` tag (often ``current``)

Before running this script,
make sure you have configured your environment so it is aware of the LSST stack
(often by ``source``\ ing a ``loadLSST.bash`` script;
however you did it, ``EUPS_PATH`` should be set),
and ``setup pipe_drivers``.
An example usage, which will install the master branch and tag it as ``current`` is::

    foo@bar:~/pfs/pfs_pipe2d/bin $ build_pfs.sh -t current


Install manually from GitHub
----------------------------

Manual installation is the least-recommended method of installing the PFS 2D DRP pipeline,
because it is labor intensive
and can be done in different ways, making installation problems more difficult to debug.
However, it may provide a successful installation when the scripts fail
(this is essentially what the scripts attempt to do).
If you have problems, see :ref:`help`
or try an alternative installation method [#]_.

.. [#] We recommend `Using Docker`_, as that completely eliminates build problems.

Manual installation is achieved by first installing the LSST stack
and then installing the PFS packages on top.

Install LSST
^^^^^^^^^^^^

Follow the `LSST install instructions`_.
Make sure you install the correct version of the LSST stack
(currently, we use ``v18_1_0``).
Instead of installing the ``lsst_distrib`` product,
you can install just ``pipe_drivers`` for a faster install [#]_.
Follow their instructions for configuring your environment,
and ``setup pipe_drivers``.

.. _LSST install instructions: https://pipelines.lsst.io/install/newinstall.html
.. [#] You may also want to install the ``display_ds9`` and/or ``display_matplotlib`` products,
       if you intend to use the ``lsst.afw.display`` functionality.

Install PFS packages
^^^^^^^^^^^^^^^^^^^^

Install the following PFS packages, in this order:

* `pfs_utils`_
* `datamodel`_
* `obs_pfs`_
* `drp_pfs_data`_ [#]_
* `drp_stella`_
* `pfs_pipe2d`_ [#]_

.. _pfs_utils: https://github.com/Subaru-PFS/pfs_utils
.. _datamodel: https://github.com/Subaru-PFS/datamodel
.. _obs_pfs: https://github.com/Subaru-PFS/obs_pfs
.. _drp_pfs_data: https://github.com/Subaru-PFS/drp_pfs_data
.. _drp_stella: https://github.com/Subaru-PFS/drp_stella
.. _pfs_pipe2d: https://github.com/Subaru-PFS/pfs_pipe2d
.. [#] The ``drp_pfs_data`` package requires use of ``git-lfs``.
.. [#] The ``pfs_pipe2d`` package is not strictly necessary for running the PFS 2D DRP,
       but it contains the integration test, which is useful for validating the installation.

Installation of each package involves:

1. Download the package.
   You can either use ``git``::

       git clone http://github.com/Subaru-PFS/<packageName>

   or you can download the package directly::

       curl -Lfk https://api.github.com/repos/Subaru-PFS/<packageName>/tarball/master | tar xvz


2. Change into the package directory.
3. Put the package into your environment::

       setup -k -r .

   Note the use of the ``-k`` flag,
   which tells :ref:`eups` to *keep* the current versions of any dependencies you've configured
   (so versions won't change underneath you).

4. Build and install the package::

       scons install declare --tag=current

   (The use of ``--tag=current`` is optional,
   but it makes it easier to select later.)

5. Put the installed version of the package into your environment::

       setup <packageName>

   You may also need to specify a version or tag name to select the correct version.


Testing your installation
-------------------------

The ``pfs_pipe2d`` package includes an integration test,
which should run all the way through if your installation is working.

First, be sure you've loaded the pipeline software into your environment::

    eups list -s pfs_pipe2d

If that generates an error
(``eups list: Unable to find product pfs_pipe2d tagged "setup"``)
then you need to load the pipeline software into your environment::

    setup pfs_pipe2d

Now, you should be able to be able to access ``pfs_integration_test.sh``.
The usage information is::

    Exercise the PFS 2D pipeline code

    Usage: /home/pfs/pfs/pfs_pipe2d/bin/pfs_integration_test.sh [-b <BRANCH>] [-r <RERUN>] [-d DIRNAME] [-c CORES] [-n] <PREFIX>

        -b <BRANCH> : branch of drp_stella_data to use
        -r <RERUN> : rerun name to use (default: 'integration')
        -d <DIRNAME> : directory name to give data repo (default: 'INTEGRATION')
        -c <CORES> : number of cores to use (default: 1)
        -G : don't clone or update from git
        -n : don't cleanup temporary products
        <PREFIX> : directory under which to operate

The main options you should care about are
``-c`` (more cores makes it go a bit faster; but you won't see much gain beyond about 4 cores)
and the ``PREFIX`` positional argument (where to do the test).
The ``-b`` option is for developers testing new features.
The ``-r`` and ``-d`` allow different runs of the integration test in the same directory.
Don't use the ``-G`` option unless you know what you're doing.
The ``-n`` option keeps some temporary products around, at the cost of more disk usage.

We recommend running the integration test something like this::

    mkdir -p /path/to/integrationTest
    cd /path/to/integrationTest
    pfs_integration_test.sh -c 4 .
