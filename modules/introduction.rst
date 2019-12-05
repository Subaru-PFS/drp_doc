.. introduction:

Introduction
------------

The `Prime Focus Spectrograph`_ consists of approximately 2400 science fibers,
distributed over a 1.3 deg\ :sup:`2` field,
feeding four spectrographs, each comprised of blue, red and infrared arms
which together cover wavelengths of 0.38 - 1.26 microns.
It is the responsibility of the 2D Data Reduction Pipeline (DRP) to process the raw data
to produce wavelength-calibrated, flux-calibrated coadded spectra suitable for science investigations.
This document outlines the major algorithmic modules for the 2D DRP.

.. _Prime Focus Spectrograph: https://pfs.ipmu.jp

The data flow of the science pipeline is presented in the 2D DRP Design document,
but here we give a summary for background.
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

The general flow of the pipeline has been `implemented`_
with simple placeholder implementations for the algorithmic modules
that perform the necessary functions in a sub-optimal manner.
It is now our goal to improve the algorithmic quality of these modules.
These will be developed under the `drp_stella`_ package,
and written in `Python`_ [#]_.
As far as is practical given the smaller size of our development team,
we will follow the coding styles and policies in the `LSST Developer Guide`_.

.. _implemented: https://pfspipe.ipmu.jp/jira/browse/PIPE2D-310
.. _drp_stella: https://github.com/Subaru-PFS/drp_stella
.. _Python: https://www.python.org

.. [#] Classes and functions requiring the performance of a compiled language
       can be implemented in `C++`_ and wrapped using `pybind11`_.

.. _C++: https://en.wikipedia.org/wiki/C%2B%2B
.. _pybind11: https://github.com/pybind/pybind11
.. _LSST Developer Guide: https://developer.lsst.io


These algorithmic modules will be implemented as subclasses of |Task|_,
as the configuration framework we use allows these to be substituted at runtime,
so long as the call signature matches.
It is the purpose of this document to specify these call signatures
so that multiple algorithmic modules of each kind can be developed and employed as required.
The call signatures specified in this documents are based on the current pipeline implementation which,
because it currently uses only placeholder algorithms,
may not be sufficient to implement more complicated algorithms
(e.g., a data butler is required in order to load important data,
but none is present in the current call signature).
We therefore welcome proposals to extend or correct the call signatures in this document,
but these proposals should be discussed by the DRP team
and this document updated
before the proposal is implemented.

.. |Task| replace:: ``lsst.pipe.base.Task``
.. _Task: https://github.com/lsst/pipe_base/blob/master/python/lsst/pipe/base/task.py

Several modules are expected to return a "persistable object",
which means an object of a custom class which can be persisted with the LSST data butler.
We will use the ``FitsCatalogStorage`` storage type [#]_,
which requires the following methods::

    class SomePersistable:
        @classmethod
        def readFits(cls, filename):
            """Read from FITS file

            Parameters
            ----------
            filename : `str`
                Filename to read.

            Returns
            -------
            self : ``cls``
                Object read from FITS file.
            """
            # Use astropy.io.fits to open and read FITS file, then construct object
            return cls(stuff)

        def writeFits(self, filename):
            """Write to FITS file

            Parameters
            ----------
            filename : `str`
                Name of file to which to write.
            """
            # Use astropy.io.fits to write FITS file.



.. [#] There are other storage types that can be used,
       but ``FitsCatalogStorage`` has a clear API,
       and FITS allows portability.
       Despite the name, ``FitsCatalogStorage`` does not mean that a FITS table must be used
       (an image can be used as the format if desired);
       instead, it refers to the API used to read and write the file.


The following classes are useful building blocks of the algorithmic modules:

* ``pfs.datamodel.PfsSpectra``:
  a collection of spectra from a common source
  (e.g., an arm, or an entire exposure).
  This is the base class of the ``pfsArm`` and ``pfsMerged`` files.
  Useful attributes include:

  + ``wavelength``: wavelength array (nm), of dimension ``NxM`` for ``N`` spectra of length ``M``.
  + ``flux``: flux array (counts or nJy), of dimension ``NxM``.
  + ``mask``: mask array, of dimension ``NxM``.
  + ``sky``: sky array, of dimension ``NxM`` (not currently used).
  + ``covar``: covariance array (central 3 diagonals of the full covariance matrix),
    of dimension ``Nx3xM`` (not currently set properly).
  + ``flags``: a mask interpreter.

  Useful methods include:

  + ``plot``: plot the spectra using matplotlib.
  + ``resample``: resample the spectra to a common wavelength vector.
  + ``extractFiber``: pull out the spectrum from a single fiber into a ``PfsSpectrum``.

* ``pfs.datamodel.PfsSimpleSpectrum``:
  the spectrum for a single object.
  This is intended to hold model spectra,
  and is the base class of the ``pfsReference`` files.
  Useful attributes include:

  + ``wavelength``: wavelength array (nm), of dimension ``M``.
  + ``flux``: flux array (counts or nJy), of dimension ``M``.
  + ``mask``: mask array, of dimension ``M``.
  + ``flags``: a mask interpreter.

  Useful methods include:

  + ``plot``: plot the spectrum using matplotlib.

* ``pfs.datamodel.PfsSpectrum``:
  similar to ``PfsSimpleSpectrum``,
  this is the spectrum for a single object,
  but it is suitable for spectra from observations.
  This is the base class of the ``pfsSingle`` and ``pfsObject`` files.
  Useful attributes include:

  + ``wavelength``: wavelength array (nm), of dimension ``M``.
  + ``flux``: flux array (counts or nJy), of dimension ``M``.
  + ``mask``: mask array, of dimension ``M``.
  + ``sky``: sky array, of dimension ``NxM``.
  + ``covar``: covariance array (central 3 diagonals of the full covariance matrix),
    of dimension ``3xM`` (not currently set properly).
  + ``covar2``: a low-resolution non-sparse covariance estimate (not currently set properly).
  + ``flags``: a mask interpreter.

  Useful methods include:

  + ``plot``: plot the spectrum using matplotlib.

* ``pfs.datamodel.PfsConfig``:
  configuration of the top-end,
  including the mapping of fibers to objects.
  Useful attributes include:

  + ``fiberId``: array of fiber identifier.
  + ``ra``: Right Ascension (degrees) for each fiber.
  + ``dec``: = Declination (degrees) for each fiber.
  + ``targetType``: target type (an integer, with values from ``pfs.datamodel.TargetType``) for each fiber.
  + ``fiberMag``: magnitudes (an array, order matching that of the ``filterNames``) for each fiber.
  + ``filterNames``: filter names (a list, order matching that of the ``fiberMag``) for each fiber.
  + ``pfiNominal``: nominal position (x,y) for each fiber.
  + ``pfiCenter``: measured position (x,y) for each fiber.

  Useful methods include:

  + ``selectByTargetType``: return indices for fibers matching a particular target type.
  + ``selectFiber``: return index for a particular fiber identifier.
  + ``getIdentity``: return a ``dict`` identifying a particular fiber identifier.
  + ``extractNominal``: extract the nominal positions for particular fibers.
  + ``extractCenter``: extract the center positions for particular fibers.

* ``pfs.datamodel.TargetType``:
  an enumeration of target types.
  The mapping from the symbolic names to integers is an implementation detail,
  so code should always use the symbolic names rather than integers.
  The names are:

  + ``SCIENCE``: science target.
  + ``SKY``: empty sky.
  + ``FLUXSTD``: flux standard.
  + ``BROKEN``: fiber is broken.
  + ``BLOCKED``: fiber is blocked (hidden behind spot).

* ``pfs.datamodel.MaskHelper``:
  interprets the mask integers.
  The mapping from the symbolic names to mask integers is an implementation detail,
  so code should always use the symbolic names rather than integers.
  Use methods include:

  + ``get``: return the integer value given a list of symbolic names.

* ``pfs.drp.stella.FiberTrace``:
  the position and profile of the fiber trace on the image.
  These are usually collected into a ``FiberTraceSet``.
  Useful attributes include:

  + ``trace``: an image of the trace.
  + ``fiberId``: the fiber identifier.

  Useful methods include:

  + ``extractSpectrum``: extract a spectrum from the image.
  + ``constructImage``: construct an image given a spectrum.

* ``pfs.drp.stella.DetectorMap``:
  mapping between ``(x,y)`` position on the detector and ``(fiberId,wavelength)``.
  Useful methods include:

  + ``findFiberId``: find the fiber at a position.
  + ``findPoint``: find the point on the detector for a fiber and wavelength.
  + ``findWavelength``: find the wavelength for a fiber and a row on the detector.
  + ``getWavelength``: retrieve the wavelength calibration for a fiber or all fibers.
  + ``getXCenter``: retrieve the column position for a fiber or all fibers.
