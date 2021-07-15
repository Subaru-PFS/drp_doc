.. _commonArguments:

Common Command-Line Arguments
=============================

Many (all?) of the scripts use a common front-end argument parser,
which means many of the possible arguments are common across many (all?) of the scripts.
If you run a script with the ``--help`` or ``-h`` argument,
it shows what arguments are possible::

    positional arguments:
    input                 path to input data repository, relative to
                            $PIPE_INPUT_ROOT
    
    optional arguments:
    -h, --help            show this help message and exit
    --calib RAWCALIB      path to input calibration repository, relative to
                            $PIPE_CALIB_ROOT
    --output RAWOUTPUT    path to output data repository (need not exist),
                            relative to $PIPE_OUTPUT_ROOT
    --rerun [INPUT:]OUTPUT
                            rerun name: sets OUTPUT to ROOT/rerun/OUTPUT;
                            optionally sets ROOT to ROOT/rerun/INPUT
    -c [NAME=VALUE [NAME=VALUE ...]], --config [NAME=VALUE [NAME=VALUE ...]]
                            config override(s), e.g. -c foo=newfoo bar.baz=3
    -C [CONFIGFILE [CONFIGFILE ...]], --configfile [CONFIGFILE [CONFIGFILE ...]]
                            config override file(s)
    -L [LEVEL|COMPONENT=LEVEL [LEVEL|COMPONENT=LEVEL ...]], --loglevel [LEVEL|COMPONENT=LEVEL [LEVEL|COMPONENT=LEVEL ...]]
                            logging level; supported levels are
                            [trace|debug|info|warn|error|fatal]
    --longlog             use a more verbose format for the logging
    --debug               enable debugging output?
    --doraise             raise an exception on error (else log a message and
                            continue)?
    --noExit              Do not exit even upon failure (i.e. return a struct to
                            the calling script)
    --profile PROFILE     Dump cProfile statistics to filename
    --show SHOW [SHOW ...]
                            display the specified information to stdout and quit
                            (unless run is specified).
    -j PROCESSES, --processes PROCESSES
                            Number of processes to use
    -t TIMEOUT, --timeout TIMEOUT
                            Timeout for multiprocessing; maximum wall time (sec)
    --clobber-output      remove and re-create the output directory if it
                            already exists (safe with -j, but not all other forms
                            of parallel execution)
    --clobber-config      backup and then overwrite existing config files
                            instead of checking them (safe with -j, but not all
                            other forms of parallel execution)
    --no-backup-config    Don't copy config to file~N backup.
    --clobber-versions    backup and then overwrite existing package versions
                            instead of checkingthem (safe with -j, but not all
                            other forms of parallel execution)
    --no-versions         don't check package versions; useful for development
    --id [KEY=VALUE1[^VALUE2[^VALUE3...] [KEY=VALUE1[^VALUE2[^VALUE3...] ...]]
                            data IDs, e.g. --id visit=12345 ccd=1,2^0,3
    
    Notes:
                * --config, --configfile, --id, --loglevel and @file may appear multiple times;
                    all values are used, in order left to right
                * @file reads command-line options from the specified file:
                    * data may be distributed among multiple lines (e.g. one option per line)
                    * data after # is treated as a comment and ignored
                    * blank lines and lines starting with # are ignored
                * To specify multiple values for an option, do not use = after the option name:
                    * right: --configfile foo bar
                    * wrong: --configfile=foo bar


``input``
---------

This is the path to the data repository.
As a positional argument, it does not have any ``--whatever`` string preceding it.


``--calib``
-----------

This is the path to the calib repository.
It *should* default to a ``CALIB`` subdirectory of the data repository,
but we've seen instances where that is broken,
so we encourage you to list it explicitly.

``--output``
------------

This specifies a directory which will become a data repository holding the outputs of the script.
This is useful for writing the outputs to a different destination than the inputs,
but in general we recommend using the ``--rerun`` option instead.

``--rerun``
-----------

This specifies a symbolic name for the processing you're undertaking.
The output data will then be written to ``<input>/rerun/<rerunName>`` in the data repository.
This defaults to your username,
which is helpful for avoiding mixups in output products between different users,
but in general we recommend using something like ``--rerun <username>/<projectName>``
(e.g., ``--rerun price/pipe2d-310``),
as that gives the output products an informative name that can be used later to identify what it is.

You can also specify separate input and output rerun names,
separated by a colon.
This is useful for when you want to build on the results from one rerun,
but want to write to a separate directory,
e.g., ``--rerun price/pipe2d-310:price/pipe2d-310-tweak``.

``--config`` and ``-c``
-----------------------

These allow you to dynamically modify the configuration that will be used in the processing,
directly on the command-line,
by specifying (potentially) multiple configuration ``keyword=value`` pairs.
This is very convenient for testing how configuration tweaks modify the processing.
The trick, of course, is identifying the appropriate configuration keyword names;
for that, try ``--show config``.

The values must be plain-old-data (string/integer/float);
for more complicated configuration settings,
see ``--configfile`` and ``-C``.

``--configfile`` and ``-C``
---------------------------

These allow you to dynamically modify the configuration that will be used in the processing,
by specifying a configuration override file.
The configuration override file is written in python,
modifying an implicitly-declared value called ``config``,
which is the configuration tree.
This allows you to change the values in a list,
or set values programmatically using code,
e.g.::

    config.foo.masks = ["NO_DATA", "SAT", "BAD"]
    for thingy in (config.foo.thingy, config.bar.thingy):
        thingy.whatsit = "gizmo"

It also allows for the substitution of modules using the ``retarget`` method,
e.g.::

    from pfs.drp.stella.alternativeImpl import AlternativeTask
    config.foo.retarget(AlternativeTask)

As with ``--config``/``-c``,
the trick is identifying the appropriate configuration keyword names;
for that, try ``--show config``.

``--loglevel`` and ``-L``
-------------------------

These change the verbosity level of the logging.
You can set the logging level globally (for all logging) by specifying the new logging level;
or just override the logging level for a single component by ``<component>=<level>``.
The logging levels, in order of decreasing verbosity are:
``trace``,
``debug``,
``info``,
``warn``,
``error``,
``fatal``.

The default logging level is ``info``.
If you're having trouble figuring out why something is happening,
try ``-L debug``.
If you're getting too much output to the screen, try ``-L warn``.

If you want to change just a single component,
the logging name should be present in the log messages;
it should also be the same as for corresponding entry in the configuration tree
(without the leading ``config.``, of course).


``--longlog``
-------------

This enables a longer format for the logging messages.

``--debug``
-----------

This enables debugging output from the pipeline,
which might include plots or image displays.
This requires putting a file named ``debug.py`` somewhere on your ``PYTHONPATH``,
with contents similar to the following::

    try:
        import lsstDebug
        print("Importing debug settings...")
        def DebugInfo(name):
            di = lsstDebug.getInfo(name)  # Note: lsstDebug.Info(name) would call us recursively
            if name in (
    #                    "pfs.drp.stella.fitContinuum",
                        ):
                di.display = True
                di.plot = True
            elif name in (
                        "pfs.drp.stella.calibrateWavelengthsTask",
                        ):
                di.display = True
                di.showArcLines = True
                di.showFibers = range(3000)
                di.plotWavelengthResiduals = True
                di.plotArcLinesLambda = True
                di.arc_frame = 1
        lsstDebug.Info = DebugInfo
        lsstDebug.frame = 1
    except ImportError:
        import sys
        print("Unable to import lsstDebug;  not setting display intelligently", file=sys.stderr)

Unfortunately, there's not a good catalog of what settings are possible,
so setting this up usually requires knowledge of the code.
But if you're using this then you're probably fixing some code, so you'll be able to figure that out.


``--doraise``
-------------

This has the script raise an exception in the event of an error,
rather than swallowing the exception and attempting to push on.
This is useful in combination with the ``pdb`` debugger::

    python -m pdb $(which reduceExposure.py) ... --doraise

will run ``reduceExposure.py`` and put drop you into the debugger when it hits the exception
(it does start you off in the debugger;
tell it ``c`` to continue,
and then it will run the program until it hits the exception).


``--noExit``
------------

You can generally ignore this one.


``--profile``
-------------

This runs the main operation under ``cProfile``,
and dumps the profile statistics to the provided filename.
You can then get a basic profile in python::

    >>> from pstats import Stats
    >>> stats = Stats("myStats.dat")  # Or whatever your filename was
    >>> stats.sort_stats("cumulative")
    >>> stats.print_stats(30)  # Print top 30

This probably won't work well with the MPI-based scripts,
but they have their own way of dumping profile statistics.

``--show``
----------

This provides information about what the script is going to operate on,
and how it's configured.
This argument takes one or more keywords:

* ``config[=PATTERN]``: Show the configuration tree, or just the entries that match the glob pattern.
* ``history=PATTERN``: Show where the configuration entries that match the glob pattern were set.
* ``tasks``: Show the task hierarchy.
* ``data``: Show the data that will be processed.
* ``run``: Continue running after showing whatever was requested;
  if this is not specified, the script will exit.


``-j``
------

This provides for parallelisation of the processing.
Specify the number of processes to use.

This does not work with MPI-based scripts,
but they have their own way of doing parallelisation (e.g., ``--cores``).


``--timeout`` and ``-t``
------------------------

This specifies the maximum wall time in seconds for the processing when running in parallel.
This should be set to a very large number so that it never needs to be modified.


``--clobber-output``
--------------------

This removes and recreates the output directory if it already exists.
I've never used it, so I'm not sure it works.


``--clobber-config``
--------------------

The scripts save their configuration tree,
and if a configuration tree has already been saved then they check to see if there's any difference.
This helps prevent accidental mixing of multiple configuration settings in a single output.
If this argument is specified,
then instead of checking for configuration differences,
the script will clobber the existing saved configuration tree.

.. danger:: In general, this argument should **never** be used during production.
            It is acceptable to use this when developing or debugging,
            using a separate output directory or rerun.


``--no-backup-config``
----------------------

When ``--clobber-config`` is used,
the script will make a backup copy of the old (clobbered) configuration.
This argument disables that behaviour.


``--clobber-versions``
----------------------

The scripts save information on the software versions being used,
and if this information has already been saved then they check to see if there's any difference.
This helps prevent accidental mixing of multiple versions in a single output.
If this argument is specified,
then instead of checking for configuration differences,
the script will clobber the existing saved software version information.

.. danger:: In general, this argument should **never** be used during production.
            It is acceptable to use this when developing or debugging,
            using a separate output directory or rerun.


``--no-versions``
-----------------

If this argument is specified,
no check will be made for software version differences.

.. danger:: In general, this argument should **never** be used during production.
            It is acceptable to use this when developing or debugging,
            using a separate output directory or rerun.


``--id``
--------

This argument specifies the data to be processed.
Whenever a pipeline command takes an ``--id`` argument,
*any* set of keyword-value pairs can be used that makes sense.
For example, one can specify an explicit list of visits
(either joining individual values with a caret, ``^``,
or specifying a range with ``..``)::

    --id visit=1^2^3^4^5
    --id visit=1..5

or specifying every second one::

    --id visit=2^4^6^8^10
    --id visit=2..10:2

Alternatively, other keywords can be used if that is sufficient to uniquely identify the data::

    --id field=BIAS dateObs=2019-01-11

would select all bias exposures from 2019-01-11.

The following keywords are currently supported:

* ``site`` (string): where the data was obtained:

  + ``J``: JHU
  + ``L``: LAM
  + ``X``: Subaru offline
  + ``I``: IPMU
  + ``A``: ASIAA
  + ``S``: Summit
  + ``P``: Princeton
  + ``F``: Simulation ("fake")

* ``category`` (string): category of data:

  + ``A``: science
  + ``B``: NTR
  + ``C``: Meterology
  + ``D``: HG

* ``field`` (string): the field target (usually recorded by the observer).
* ``expId`` (integer): the exposure identifier (an alias for ``visit``) [#]_.
* ``visit`` (integer): the exposure identifier.
* ``ccd`` (integer): the CCD identifier (unique combination of ``spectrograph`` and ``arm``).
* ``filter`` (string): an alias for ``arm`` [#]_.
* ``arm`` (string): the arm of the spectrograph:

  + ``b``: Blue
  + ``r``: Red
  + ``m``: Medium-resolution, red.
  + ``n``: Near infrared.

* ``spectrograph`` (integer): the spectrograph module number (1-4).
* ``dateObs`` (string): the date of observation (YYYY-MM-DD).
* ``expTime`` (float): the exposure time (sec).
* ``dataType`` (string): type of data (e.g., bias, dark, flat, science).
* ``taiObs`` (string): date+time of observation (YYY-MM-DDTHH:MM:SS.sss).
* ``pfiDesignId`` (int): the top-end configuration design identifier.
* ``dither`` (float): slit offset in spatial dimension.
* ``shift`` (float): slit offset in spectral dimension.
* ``focus`` (float): focus offset.
* ``lamps`` (string): calibration lamps that are active.
* ``attenuator`` (float): attenuator setting.
* ``photodiode`` (float): photodiode reading.


.. [#] We would like to get rid of ``visit``, but it is baked into the current
       version of the data butler.
.. [#] ``filter`` doesn't make much sense for a spectrograph, but it is required
       by the current version of the data butler.
