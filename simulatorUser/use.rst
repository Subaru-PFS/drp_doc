.. _use:

Using the Simulator
===================

The main interface is a script to generate a single image.
There is also a script that will generate a small dataset
for testing the pipeline.

The first time the Simulator is run, it will generate a PSF model and cache it;
this can take about an hour.
Subsequent executions will be much faster.

Initial setup
-------------

``makePfsDesign``
~~~~~~~~~~~~~~~~~

The simulator requires a ``pfsDesign``
file to tell it for which fibers are assigned to which sources.
If there is not such a file available, one can generate that using the
``makePfsDesign`` command::

    makePfsDesign --fibers lam --pfsDesignId 1 --scienceCatId 1 --scienceObjId "18 55 71 76 93 94 105 112 115"

The above command generates a file ``pfsDesign-0x0000000000000001.fits``,
corresponding to a ``pfsDesignId`` of ``1``,
mapping randomly objects with object identifiers listed
in the value for the ``--scienceObjId`` option.
These object identifiers are associated with a catalogue '``1``'
(the value of ``--scienceCatId``).
The simulator will then look under
the directory 1 (the scienceCatId) for the input spectra.

The ``--fibers`` option allows the user to specify which fibers
are illuminated from a set of combinations listed below:

* ``one``: fiber 315 only.
* ``two``: fibers 311 and 315 only.
* ``lam``: fibers 2, 65, 191, 254, 315, 337, 400, 463, 589, 650.
* ``odd``: every other fiber, starting with the first.
* ``even``: every other fiber, starting with the second.
* ``all``: all fibers.

``DRP_INSTDATA_DIR``
~~~~~~~~~~~~~~~~~~~~

Also before running the simulator the envionment variable ``DRP_INSTDATA_DIR``
needs to be set to point
to a recent version of the ``drp_instdata`` git repository. For example::

    cd /path/to
    git clone https://github.com/Subaru-PFS/drp_instdata.git
    setup -jr drp_instdata

Location of input spectra
~~~~~~~~~~~~~~~~~~~~~~~~~

The main simulator command, ``makeSim``, requires
the corresponding object spectra
as input. More specifically, the location of those input spectra.
While this can be specified through the ``--spectraDir`` option, an alternative
is to use the default value (which is the current working directory)
and could create a symbolic link to your spectral files.
For example, if your input data are the ``lowz_COSMOS`` data
from the ``drp_instdata`` repository, you could create a link as follows::

    ln -s /path/to/drp_instdata/data/objects/lowz_COSMOS/ 1

where the ``1`` corresponds to the catalogue identifer
of the source (ie the value of the ``scienceCatId``
in the ``makePfsDesign`` example shown above).


Single image
------------

The ``makeSim`` script runs the Simulator to produce a single image
and the associated ``pfsConfig`` file.
An example command-line is::

    makeSim --detector r1 --pfsConfig --pfsDesignId 1 --exptime 0 --domeClosed --expId 0 --imagetyp BIAS

The ``--detector`` specifies the spectrograph and arm;
we currently only support ``r1`` and ``b1``.

The ``-pfsConfig`` determines whether a pfsConfig file will be
generated and written to file or not.

The ``--pfsDesignId`` specifies the fiber setup. You need to have a
``pfsDesign-0xNNNNNNNNNNNNNNNN.fits`` file present
in the current working directory,
where ``NNNNNNNNNNNNNNNN`` is the 16-digit
hexadecimal representation of the designId you have
specified in the ``--pfsDesignId`` argument.

``--exptime`` specifies the exposure time in seconds.
This is used to scale the input spectrum.

``--domeClosed`` determines whether the sky background is
included or not.
If present, the sky background will not be included.

``--expId`` specifies the exposure identifier to use.
This is used in the filename.

``--imagetyp`` specifies the image type.
This is used in the header. Allowed values are
BIAS, DARK, FLAT, ARC and OBJECT.

``--allOutput`` specifies that the Simulator
should write additional FITS extensions
containing information.

``--pdb`` specifies that the program should drop into the
debugger in the event of an exception.

There are additional arguments, which will be provided in
future releases of this document.

Multiple images
---------------

The ``makeSimRun`` command calls ``makeSim`` repeatedly
in order to generate a dataset containing:

* 10 biases
* 10 darks
* 11 dithered flats
* 1 Ne arc
* 2 science exposures

This requires one parameter (the ``pfsDesignId``
corresponding to the pfsDesign to use) and an optional second parameter
(a second ``pfsDesignId`` corresponding to another pfsDesign for a
single dome-open, 900-second exposure).
