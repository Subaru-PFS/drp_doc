.. _use:

Using the Simulator
===================

The main interface is a script to generate a single image.
There is also a script that will generate a small dataset for testing the pipeline.

The first time the Simulator is run, it will generate a PSF model and cache it;
this can about an hour.
Subsequent executions will be much faster.


Single image
------------

The ``makeSim`` script runs the Simulator to produce a single image
and the associated ``pfsConfig`` file.
An example command-line is::

    makeSim --detector r1 --field lamObj --exptime 900 --expId 32 --imagetyp OBJECT --allOutput --pdb

The ``--detector`` specifies the spectrograph and arm;
we currently only support ``r1``.

The ``--field`` specifies the fiber setup.
There are several possibilities,
defined in the ``python/pfs_instmodel/examples/sampleField.py`` file.
The names typically consist of two parts:
what set of fibers is illuminated,
and what those fibers are targeting.
The set of fibers may be:

* ``one``: fiber 315 only.
* ``two``: fibers 311 and 315 only.
* ``lam``: fibers 2, 65, 191, 254, 315, 337, 400, 463, 589, 650.
* ``odd``: every other fiber, starting with the first.
* ``even``: every other fiber, starting with the second.
* ``all``: all fibers.

The targets may be:

* ``Arc``: an arc spectrum with all lamps for all fibers.
* ``Ne``: an arc spectrum with the Ne lamp for all fibers.
* ``Hg``: an arc spectrum with the Hg lamp for all fibers.
* ``Flat``: a quartz spectrum for all fibers.
* ``Comb``: a set of emission lines of equal spacing for all fibers.
* ``Const``: a constant :math:`F_nu` spectrum for all fibers.
* ``Sky``: a pure sky spectrum for all fibers.
* ``Obj``: a combination of sky, flux calibration sources and objects.

``--exptime`` specifies the exposure time in seconds.
This is used to scale the input spectrum.

``--expId`` specifies the exposure identifier to use.
This is used in the filename.

``--imagetyp`` specifies the image type.
This is used in the header.

``--allOutput`` specifies that the Simulator
should write additional FITS extensions
containing information.

``--pdb`` specifies that the program should drop into the debugger in the event of an exception.

There are additional arguments,
but I don't know what's working and what's not.


Multiple images
---------------

The ``makeSimRun`` command calls ``makeSim`` repeatedly
in order to generate a dataset containing:

* 10 biases
* 10 darks
* 11 dithered flats
* 1 Ne arc
* 2 science exposures

The only parameter to ``makeSimRun`` is a keyword specifying which fibers to use,
as above (``one``, ``two``, ``lam``, ``odd``, ``even``, ``all``).
