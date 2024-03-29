.. _buildingBlocks:

Building Blocks
===============

The pipeline is constructed from a modest number of python classes [#]_
as the building blocks of the algorithmic modules.
The classes are defined in both the ``datamodel`` and ``drp_stella`` packages;
those in ``datamodel`` are of general purpose, intended for consumption by developers and science users,
while those in ``drp_stella`` are more directed towards extracting the spectrum from the image.
Here, we give an introduction to these classes.
We regret that we do not currently have a full reference document with the various APIs,
but we hope this will be useful for those seeking to use the outputs of the pipeline,
or do development on the pipeline itself.

.. [#] Some are implemented in C++ for efficiency and/or historical reasons,
       but have been wrapped into python.


``pfs.datamodel.PfsFiberArraySet``
----------------------------------

``PfsFiberArraySet`` is a collection of spectra from a common source
(e.g., an arm, or an entire exposure).
This is the base class of the ``pfsArm`` and ``pfsMerged`` files.
Useful attributes include:

* ``wavelength``: wavelength array (nm), of dimension ``NxM`` for ``N`` spectra of length ``M``.
* ``flux``: flux array (counts or nJy), of dimension ``NxM``.
* ``mask``: mask array, of dimension ``NxM``.
* ``sky``: sky array, of dimension ``NxM``.
* ``norm``: normalisation (e.g., a quartz spectrum) of dimension ``NxM``.
* ``covar``: covariance array (central 3 diagonals of the full covariance matrix),
  of dimension ``Nx3xM`` (not currently set properly).
* ``flags``: a mask interpreter.
* ``normFlux``: a ``property`` that provides the ``flux`` divided by ``norm``.

Useful methods include:

* ``plot``: plot the spectra using matplotlib.
* ``resample``: resample the spectra to a common wavelength vector.
* ``extractFiber``: pull out the spectrum from a single fiber into a ``PfsSpectrum``.


.. _PfsSimpleSpectrum:

``pfs.datamodel.PfsSimpleSpectrum``
-----------------------------------

``PfsSimpleSpectrum`` represents the spectrum for a single object.
This is intended to hold model spectra,
and is the base class of the ``pfsReference`` files.
Useful attributes include:

* ``wavelength``: wavelength array (nm), of dimension ``M``.
* ``flux``: flux array (counts or nJy), of dimension ``M``.
* ``mask``: mask array, of dimension ``M``.
* ``flags``: a mask interpreter.

Useful methods include:

* ``plot``: plot the spectrum using matplotlib.


``pfs.datamodel.PfsFiberArray``
-------------------------------

``PfsFiberArray`` is similar to :ref:`PfsSimpleSpectrum`.
This is the spectrum for a single object,
but it is suitable for spectra from observations.
This is the base class of the ``pfsSingle`` and ``pfsObject`` files.
Useful attributes include:

* ``wavelength``: wavelength array (nm), of dimension ``M``.
* ``flux``: flux array (counts or nJy), of dimension ``M``.
* ``mask``: mask array, of dimension ``M``.
* ``sky``: sky array, of dimension ``NxM``.
* ``covar``: covariance array (central 3 diagonals of the full covariance matrix),
  of dimension ``3xM`` (not currently set properly).
* ``covar2``: a low-resolution non-sparse covariance estimate (not currently set properly).
* ``flags``: a mask interpreter.

Useful methods include:

* ``plot``: plot the spectrum using matplotlib.


``pfs.datamodel.PfsConfig``
---------------------------

``PfsConfig`` is the configuration of the top-end,
including the mapping of fibers to objects.
Useful attributes include:

* ``fiberId``: array of fiber identifier.
* ``ra``: Right Ascension (degrees) for each fiber.
* ``dec``: Declination (degrees) for each fiber.
* ``targetType``: target type (an integer, with values from ``pfs.datamodel.TargetType``) for each fiber.
* ``fiberMag``: magnitudes (an array, order matching that of the ``filterNames``) for each fiber.
* ``filterNames``: filter names (a list, order matching that of the ``fiberMag``) for each fiber.
* ``pfiNominal``: nominal position (x,y) for each fiber.
* ``pfiCenter``: measured position (x,y) for each fiber.

Useful methods include:

* ``selectByTargetType``: return indices for fibers matching a particular target type.
* ``selectFiber``: return index for a particular fiber identifier.
* ``getIdentity``: return a ``dict`` identifying a particular fiber identifier.
* ``extractNominal``: extract the nominal positions for particular fibers.
* ``extractCenter``: extract the center positions for particular fibers.

``pfs.datamodel.FiberStatus``
-----------------------------

``FiberStatus`` is an enumeration of fiber statuses.
The mapping from the symbolic names to integers is an implementation detail,
so code should always use the symbolic names rather than integers.
The names are:

* ``GOOD``: fiber is working normally.
* ``BROKENFIBER``: fiber is broken.
* ``BLOCKED``: fiber is temporarily blocked.
* ``BLACKSPOT``: fiber is hidden behind a black spot on the PFI.
* ``UNILLUMINATED``: fiber is not illuminated.

``pfs.datamodel.TargetType``
----------------------------

``TargetType`` is an enumeration of target types.
The mapping from the symbolic names to integers is an implementation detail,
so code should always use the symbolic names rather than integers.
The names are:

* ``SCIENCE``: science target.
* ``SKY``: blank sky, used for sky subtraction.
* ``FLUXSTD``: flux standard, used for flux calibration.
* ``UNASSIGNED``: no particular target.
* ``ENGINEERING``: engineering fiber.
* ``SUNSS_IMAGING``: fiber goes to the SuNSS imaging leg.
* ``SUNSS_DIFFUSE``: fiber goes to the SuNSS diffuse leg.


``pfs.datamodel.MaskHelper``
----------------------------

``MaskHelper`` interprets the mask integers.
The mapping from the symbolic names to mask integers is an implementation detail,
so code should always use the symbolic names rather than integers.
Useful methods include:

* ``get``: return the integer value given a list of symbolic names.


``pfs.drp.stella.FiberTrace``
-----------------------------

``FiberTrace`` tracks the position and profile of the fiber trace on the image.
These are usually collected into a ``FiberTraceSet``.
Useful attributes include:

* ``trace``: an image of the trace.
* ``fiberId``: the fiber identifier.

Useful methods include:

* ``extractSpectrum``: extract a spectrum from the image.
* ``constructImage``: construct an image given a spectrum.


``pfs.drp.stella.FiberProfile``
-------------------------------

``FiberProfile`` is a measure of the profile of a fiber
(in the spatial dimension)
as a function of detector row (the spectral dimension).
These are usually collected into a ``FiberProfileSet``
(which acts like a ``dict`` mapping the fiber identifier to the appropriate ``FiberProfile``).
Useful methods include:

* ``fromImage``: construct a fiber profile from measuring an image (a ``classmethod``).
* ``plot``: plot the fiber profile.
* ``makeFiberTrace``: build a ``FiberTrace``,
  given a functional form for the center of the fiber as a function of detector row.
* ``makeFiberTraceFromDetectorMap``: build a ``FiberTrace``,
  using the detectorMap to provide the fiber center.
* ``extractSpectrum``: extract a spectrum from the image.


``pfs.drp.stella.DetectorMap``
------------------------------

``DetectorMap`` provides a mapping between ``(x,y)`` position on the detector and ``(fiberId,wavelength)``.
Useful methods include:

* ``findFiberId``: find the fiber at a position.
* ``findPoint``: find the point on the detector for a fiber and wavelength.
* ``findWavelength``: find the wavelength for a fiber and a row on the detector.
* ``getWavelength``: retrieve the wavelength calibration for a fiber or all fibers.
* ``getXCenter``: retrieve the column position for a fiber or all fibers.


We have two ``DetectorMap`` implementations:
``SplinedDetectorMap`` and ``DistortedDetectorMap``.

The ``SplinedDetectorMap`` implements the mapping
between ``(x,y)`` and ``(fiberId,wavelength)``
as a pair of splines for each fiber:

.. math::
    \lambda = f_i(y) \\
    x = g_i(y)

where :math:`\lambda` is the wavelength,
:math:`f_i` and :math:`g_i` are splines for the fiber of interest
(the mappings are one-to-one, so we can invert them)
and :math:`x` and :math:`y` are the positions according to the optical model.
This is used for the detectorMap generated from the optical model of the spectrograph,
where we know the position on the detector for spots of certain wavelengths for the different fibers.
Because this is based on the optical model used to design the instrument,
this has the advantage that we know the mapping even in regions where the signal-to-noise is low
(e.g., in regions strongly affected by the dichroic)
but is only relevant on its own for data from the simulator
(which is based on the same optical model).

The ``DistortedDetectorMap`` takes the ``SplinedDetectorMap`` from the optical model
and layers a distortion field on top,
along with an affine transform for one of the CCDs:

.. math::

   x' = P(x,y) + R(x, y) \\
   y' = Q(x,y) + S(x, y)

Where :math:`x` and :math:`y` are the positions according to the optical model,
:math:`P` and :math:`Q` are 2D polynomials,
and :math:`R` and `S` are first-order 2D polynomials in :math:`x` and :math:`y`
(i.e., an affine transform)
that are only applied when :math:`x > 2048` (i.e., the right-hand CCD).
