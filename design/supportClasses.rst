.. _supportClasses:

Supporting Classes
------------------

Besides the wide variety of primitives we can employ from LSST's Astronomical FrameWork (``afw``),
we need some additional classes focussed on support for spectroscopy.
We will not here attempt to reproduce the full API, but outline the intended capabilities and uses.

``DetectorMap``
^^^^^^^^^^^^^^^

This class models the fiber positions and wavelengths over the detector.
As of November 2018, this class models the fiber positions and wavelengths independently,
but the fiber positions and wavelengths are, in principle, a two-dimensional function:
a quartz exposure shows lines of constant slit position (i.e., the fibers),
while an arc exposure shows (broken) lines of constant wavelength (i.e., the emission lines).

The principal capabilities are:

* Identify the fiber at a point on the detector (``findFiberId``).
* Calculate the wavelength at a point on the detector (``findWavelength``).
* Calculate the point on the detector for a given fiber and wavelength (``findPoint``).
* Provides the wavelength solution for extracted spectra (``getWavelength``).
* Can serve as a foundation for identifying fibers on the image (``getXCenter``).


``FiberTrace`` and ``FiberTraceSet``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``FiberTrace`` models the fiber positions and profiles as a function of detector row.
A ``FiberTraceSet`` is a collection of ``FiberTrace``\ s.

As of November 2018, this class models the profile as a function of row as an image at native resolution
which, because the profiles are undersampled, means they cannot be shifted to a new center;
we hope to remedy this shortcoming in the future.

The principal capabilities of ``FiberTrace`` are:

* Provide an image of the trace (``getTrace``).
* Extract a spectrum from an image (``extractSpectrum``).
* Construct a model image given a spectrum (``constructImage``).


``Spectrum`` and ``SpectrumSet``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``Spectrum`` is an measure of flux as a function of wavelength.
A ``SpectrumSet`` is a collection of ``Spectrum``\ s.

``Spectrum`` contains vectors for the flux, background, wavelength, mask and covariance.
This is typically used to carry extracted spectra from observations,
but it could also be used for reference spectra in physical units.

A ``Spectrum`` is persisted as a ``PfsObject``,
while a ``SpectrumSet`` is persisted as a ``PfsSpectra``.


``LineSpreadFunction``
^^^^^^^^^^^^^^^^^^^^^^

A ``LineSpreadFunction`` is a model of the line profile of an extracted spectrum.
It can be measured by extracting the two-dimensional PSF, and
is an important ingredient for interpreting the science spectra produced by the pipeline.

The principal capabilities are:

* Calculate the spectrum of an emission line at a given wavelength.


``PfsSpectra``
^^^^^^^^^^^^^^

A ``PfsSpectra`` [#]_ is a collection of spectra from a common source,
which may be the arm of a spectrograph, or the entire instrument.
It shall be the formal I/O representation of such in the PFS Datamodel.

.. [#] This is called ``PfsArm`` as of November 2018,
   but that confuses the class and the use of the class.
   Renaming the class allows reuse of the class type for other cases where we want to group spectra.
   The dataset ``pfsArm`` shall now be of type ``PfsSpectra``.

The principal capabilities are:

* Read spectra from FITS (``read``).
* Write spectra to FITS (``write``).
* Plot spectra (``plot``).
* Carry data:

  + Wavelength arrays (``lam``)
  + Flux arrays (``flux``)
  + Mask arrays (``mask``)
  + Sky arrays (``sky``)
  + Covariance arrays (``covar``)


``PfsObject``
^^^^^^^^^^^^^

A ``PfsObject`` is a single spectrum of a particular object.
It is the formal I/O representation of such in the PFS Datamodel.

The principal capabilities are:

* Read spectrum from FITS (``read``).
* Write spectrum to FITS (``write``).
* Plot spectrum (``plot``).
* Carry data:

  + Wavelength array (``lam``)
  + Flux array (``flux``)
  + Mask array (``mask``)
  + Sky array (``sky``)
  + Covariance array (``covar``)


``PfsConfig``
^^^^^^^^^^^^^

A ``PfsConfig`` carries data about the configuration of the prime-focus instrument,
essentially tying the fiber IDs to their targets.

The principal capabilities are:

* Read data from FITS (``read``).
* Write data to FITS (``write``).
* Carry data for each fiber:

  + Object name (``str``)
  + RA (``float``; radians)
  + Dec (``float``; radians)
  + Fiber x, y position (``float``)
  + Nominal fiber x, y position (``float``)
  + Flag (``int``) indicating the fiber's use
    (e.g., ``SCIENCE``, ``SKY``, ``FLUXCAL``, ``BROKEN``, ``BLOCKED``).
  + Bandpasses and corresponding magnitudes (``dict`` mapping ``str`` to ``float``).

