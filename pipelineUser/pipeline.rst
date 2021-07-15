.. _pipeline:

Pipeline operations
===================

The flow of science data through the pipeline is shown in :numref:`pfsScience`.
Raw science exposures are processed through the ``reduceExposure`` procedure, which
removes the instrumental signatures,
models and subtracts the bright sky lines from the 2D image (``subtractSky2d``),
and extracts the spectra,
producing ``pfsArm`` files.
The ``mergeArms`` procedure takes all the  ``pfsArm`` files from a single exposure,
subtracts any residual sky emission from the 1D spectra,
and merges the spectra from the individual arms,
producing ``pfsMerged`` files.
These ``pfsMerged`` files are fed to the ``calculateReferenceFlux`` procedure, which
fits physical flux models to the flux standards,
and writes these as ``pfsReference`` files.
The ``fluxCalibrate`` procedure uses the ``pfsMerged`` and ``pfsReference`` files to
calculate and apply the flux calibration,
writing the flux calibrated single-exposure spectra as ``pfsSingle`` files.
Finally, the ``coaddSpectra`` procedure reads the ``pfsArm`` files from multiple exposures,
applies the various calibrations measured throughout the pipeline,
coadds the multiple observations of individual targets,
and writes the coadded spectra as ``pfsObject`` files.

.. _pfsScience:

.. figure:: pfsScience.pdf

   **The components of the pipeline for processing science observations.**


The pipeline has been implemented with placeholder algorithms that are sub-optimal
and that we do not expect will be used on real science data.
Use of these placeholder algorithms has allowed
the development of the full end-to-end pipeline
before the details of the final algorithms are known.
Moving forward, our principle goal is
to improve the quality of these algorithms
in preparation for processing real science data.


``detrend``
-----------

In addition to the pipeline described above,
we also provide a script that simply removes the instrumental signature from images;
this is intended to support instrumental development.
Here is an example usage::

    detrend.py /path/to/dataRepo --calib /path/to/calibRepo --rerun detrending --id visit=33

The output is a ``calexp`` file:
an image with the instrumental signatures removed (or "detrended").


``reduceExposure``
------------------

``reduceExposure.py`` reads raw images,
removes the instrumental signatures
(using the outputs of the calib pipeline),
subtracts the bright sky lines from the image,
and extracts the spectra,
writing ``pfsArm`` files::

    reduceExposure.py /path/to/dataRepo --calib /path/to/calibRepo --rerun pipeline --id field=OBJECT

The ``pfsArm`` files will likely not be of great interest for most science users.
The exception is when looking for potential contamination of one spectrum by its neighbours,
as the ``pfsArm`` preserves the sampling from the image
(i.e., no interpolation has been applied).

Because this is an important element of the pipeline
that some will want to use without the rest of the pipeline,
we provide here an overview of the operation:

* Instrument signature removal and repair (CR masking, static bad pixels)
* Wrangle spectral calibs:
    * Read ``fiberProfiles``
    * Measure line centroids
    * Read ``detectorMap``
    * Perform low-order adjustment using measured centroids
    * Write adjusted detectorMap as ``detectorMap_used``
    * Measure line fluxes
* Measure PSF and resulting LSF
* 2D sky subtraction
* Extract spectrum
    * Optional 2D continuum subtraction
* Write outputs:
    * ``calexp``: exposure, with 2D continuum subtracted if suitably configured
    * ``pfsArmLsf``: line-spread function
    * ``sky2d``: 2D sky subtraction model
    * ``pfsArm``: extracted spectra
    * ``arcLines``: line centroids+fluxes


``mergeArms``
-------------

``mergeArms.py`` reads the ``pfsArm`` files,
subtracts any residual sky from the 1D spectra,
and merges the spectra from the multiple arms [#]_,
writing the ``sky1d`` and ``pfsMerged`` files::

mergeArms.py /path/to/dataRepo --calib /path/to/calibRepo --rerun pipeline --id field=OBJECT

.. [#] We don't currently have any data with multiple arms,
       but this is part of the pipeline because ultimately we will have data with multiple arms,
       and also because this module contains the 1D sky subtraction.

The ``sky1d`` files will be used by ``coaddSpectra``.
The ``pfsMerged`` files will be used by ``calculateReferenceFlux`` and ``fluxCalibrate``.

Science users may be interested in the ``pfsMerged`` files,
since they contain the full-wavelength spectra from a single observation;
however, note that they are not flux-calibrated.


``calculateReferenceFlux``
--------------------------

``calculateReferenceFlux.py`` reads the ``pfsMerged`` files,
and fits model spectra with physical fluxes to the flux calibration targets,
writing ``pfsReference`` files::

    calculateReferenceFlux.py /path/to/dataRepo --calib /path/to/calibRepo --rerun pipeline --id field=OBJECT

The ``pfsReference`` files will be used by ``fluxCalibrate``;
we don't anticipate science users having much interest in them.


``fluxCalibrate``
-----------------

``fluxCalibrate.py`` reads the ``pfsMerged`` and ``pfsReference`` files,
fits a flux calibration model,
and writes ``fluxCal`` and ``pfsSingle`` files::

    fluxCalibrate.py /path/to/dataRepo --calib /path/to/calibRepo --rerun pipeline --id field=OBJECT

The ``fluxCal`` files will be used by ``coaddSpectra``.
The ``pfsSingle`` files are not used by the pipeline,
but may be of interest to science users:
since they contain the full-wavelength, flux-calibrated spectra from single observations,
they will be of use for those interested in spectra variability.


``coaddSpectra``
----------------

``coaddSpectra.py`` reads the ``pfsArm``, ``sky1d`` and ``fluxCal`` files [#]_,
coadds all spectra of repeat observations,
and writes ``pfsObject`` files::

    coaddSpectra.py /path/to/dataRepo --calib /path/to/calibRepo --rerun pipeline --id field=OBJECT

.. [#] The current implementation doesn't read or use the ``sky1d`` or ``fluxCal`` files.
       Whoops, sorry.

The ``pfsObject`` files are the principal science product of the 2D pipeline,
since they are the full-wavelength, flux-calibrated, coadded spectra from multiple observations.
