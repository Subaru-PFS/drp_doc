Relative Fiber Throughputs
==========================

The science mission of PFS demands accurate sky subtraction
in order to detect faint galaxy emission lines near bright sky lines,
which requires accurate and precise relative fiber throughputs.

Because the blank sky is observed by a separate set of fibers
from those recording the science targets,
we need to able to relate the relative signals of fibers across the instrument
and as a function of wavelength:
we need to be able to connect the fluxes measured
in fiber :math:`i` with the fluxes measured in fiber :math:`j`,
despite the fact that the photons come from different parts of the sky,
pass through different fibers,
different spectrographs
and are measured by different detectors.
We also need to be able to connect the fluxes measured for fiber :math:`k`
in the blue, red and NIR arms.

Prior to about January 2025,
there were significant and unpredictable changes
in the relative fiber throughputs within a run,
and even within a night.
The use of index-matching gel in the fiber connectors
appears to have greatly mitigated this problem.

Below we outline our current strategy for measuring and applying
the relative fiber throughputs.
The final result is that after running the ``ReduceExposureTask`` on a quartz exposure,
the ``pfsArm.flux`` spectra correspond to the extracted spectra from the image,
and the ``pfsArm.norm`` spectra consist of the contents of the ``fiberNorms_calib``,
with the black spot, screen illumination and PFI corrections (including the skyNorms common mode) applied.


General strategy
----------------

We use quartz exposures as a reference to connect measured signals
in different fibers, spectrographs and wavelengths.
The quartz provides a single bright light source observed simultaneously
by all fibers and spectrograph cameras.
Following the introduction of index-matching gel in the fiber connectors,
it appears to be sufficient to make this measurement once per run.

When processing a science exposure,
the measured quartz spectra are propagated to the ``pfsArm.norm`` spectra.
Corrections are applied to these to account for
the :ref:`black spot shadows <blackSpots>`
and the :ref:`screen illumination pattern <screenIllumination>`.

The quartz exposures are taken with the fibers at the ``HOME`` position,
and :ref:`additional corrections <_pfiCorrections>` are applied to account
for changes in the fiber throughput with position within the patrol region.


Measurement
-----------

We can measure the relative fiber throughputs in two ways.
The first is through quartz exposures.
These provide a high signal-to-noise measurement of the relative fiber throughputs
as a function of fiber, spectrograph and wavelength.
We call these "fiberNorms".
(We might instead use exposures of the twilight sky,
but these are less convenient to obtain and have lower signal-to-noise;
we will apply :ref:`corrections <screenIllumination>` to the quartz exposures
to make them look more like the sky.)

The second is through the sky lines in science exposures.
While these have lower signal-to-noise per exposure than the quartz exposures,
they provide a direct measurement of the quality of the sky subtraction,
revealing any residual relative fiber throughput errors,
and can be measured for many science exposures.
We call these "skyNorms".


fiberNorms
~~~~~~~~~~

The fiberNorms are measured from the ``pfsArm`` spectra of quartz exposures:

.. math::

    \tt{fiberNorms} = \tt{pfsArm.flux} / \tt{pfsArm.norm}

When generating a calibration product [#]_,
the :ref:`screen illumination correction <screenIllumination>` is applied
but the :ref:`PFI corrections <pfiCorrections>` are not applied.
When generating a product for tracking the stability of the system [#]_,
all the corrections are applied.

.. [#] The ``fiberNorms_calib`` product; see below.
.. [#] The ``fiberNorms`` product; see below.


Even if there are no changes to the system throughput,
the fiberNorms values will deviate from a mean value of unity
if the brightness of the quartz lamp changes
or if the exposure time is different.
This feature may be useful for monitoring the stability of the system,
but if it is considered annoying we may remove (and record) the median value to simplify the analysis.


skyNorms
~~~~~~~~

The "skyNorms" are a measure of the normalization of the sky lines in each fiber
relative to the model sky spectrum.
As such, they are a direct measure of the quality of the sky (line) subtraction.
They differ from the "fiberNorms" in that they are measured from science exposures
(rather than quartzes),
and are achromatic
(i.e., a single value per fiber, rather than a spectrum per fiber).

Because they are based on sky lines,
the skyNorms are best measured from fibers with minimal object flux.
Science exposures for faint extragalactic and cosmology targets are ideal
due to object spectra that do not contaminate the sky lines.
Given an extracted object spectrum and a model sky spectrum
(from the usual ``BlockedOversampledSpline`` constructed from the sky fibers in the exposure),
we subtract the continuum from both the object and sky spectra
(using the ``FitContinuumTask``).
We select pixels in the object spectrum that are bright sky lines:
unmasked, high signal-to-noise (``minSignalToNoise=10``)
with a ratio relative to the sky spectrum close to unity
(the ratio is between ``minRatio=1/2`` and ``maxRatio=2``,
and no more than ``rejectRatio=0.1`` deviant from the median ratio for that spectrum).
Then we measure the ``skyNorm`` from those pixels
using variance-weighted least-squares:

.. math::

    \textrm{skyNorm}_i = \sum_\textrm{pixels} f_i s_i / \sum_\textrm{pixels} s_i^2

where
:math:`\textrm{skyNorm}_i` is the skyNorm for fiber :math:`i`,
:math:`f_i` is the object spectrum for fiber :math:`i`,
and :math:`s_i` is the sky spectrum for fiber :math:`i`,
and the sums are over the selected pixels.
This calculation is performed iteratively with sigma clipping
(``iterations=3 rejection=3.0``)
to remove outlier pixels.

We currently believe the skyNorms are mostly achromatic [#]_ :
plotting the skyNorms from the ``r`` arm against skyNorms from the ``b`` arm
yields a straight line with a slope of unity
and a standard deviation about the line of about 1%.
A single skyNorm value per fiber is therefore calculated
using data from multiple arms simultaneously.

.. [#] We suspect the skyNorms may be chromatic in the presence of vignetting
       by, e.g., dust spots, but this is yet to be demonstrated in the data.


Data products
~~~~~~~~~~~~~

``fiberNorms_calib`` is the fiberNorms calibration product.
It is created by the ``fiberNorms.yaml`` pipeline,
by combining multiple [#]_ ``pfsArm`` spectra of quartzes.
This provides a high-quality quartz spectrum for use in calibration of science exposures.

.. [#] Usually consecutive exposures, assuming the quartz lamp is stable.

Note that the values of the fiberNorms depend on
the choice of ``fiberProfiles`` used in the spectral extraction.
In order to protect the user against using ``fiberNorms_calib``
that are not appropriate for a given ``pfsArm``,
we record a hash of the ``fiberProfiles`` used for the extractions,
and check that the hashes are consistent.

``fiberNorms`` is a product created by the ``observing.yaml`` pipeline
for quartz exposures only.
It contains the ratio of the new quartz to the reference quartz in the ``fiberNorms_calib``,
allowing for tracking of the stability of the system.

``skyNorms_calib`` product is the skyNorms calibration product,
a "common mode" correction derived from many science exposures over a run.
It is created by the ``skyNorms.yaml`` pipeline.
That pipeline also generates a ``skyNorms`` product for each science exposure it operates on;
these are useful as data for modeling the variation of the skyNorms with fiber position.


Corrections
-----------

Multiple corrections are applied to the normalizations
to attempt to model out different effects on the relative fiber throughputs.

Note that all the corrections are applied to the ``pfsArm.norm`` rather than ``pfsArm.flux``,
because we want ``pfsArm.flux`` to be identical to the spectra extracted from the image.
The goal is that the ``pfsArm.flux/pfsArm.norm`` values will be
corrected for relative throughput differences.


.. _blackSpots:
Black spots
~~~~~~~~~~~

This correction attempts to account for the shadow of the black spots on the fibers.
It is simplistic and inaccurate,
and we therefore strive to keep fibers out of the shadow of the black spots
in order to avoid adding systematic errors.
The correction is a linear function of the distance of the fiber from the black spot
(which is known to be a poor approximation of the more complicated geometry of the shadows):

.. math::

    c_{\rm bs} & = \textrm{max}(1 - m(r - d), 0) & {\rm if}\ d < r

    c_{\rm bs} & = 1 & {\rm if}\ d \geq\ r

where :math:`m = 1.108` is the slope of the correction (in mm\ :sup:`-1`),
:math:`r = 1.232` is the radius of the black spot shadow (in mm),
and :math:`d` is the distance of the fiber from the center of the black spot (in mm).

The black spot correction is applied within the ``ReduceExposureTask``,
by the ``pfs.drp.stella.blackSpotCorrection.BlackSpotCorrectionTask``,
if the configuration parameter ``reduceExposure:doBlackSpotCorrection=True``.
The value of the correction for each fiber is written to the ``pfsArm.notes.blackSpotCorrection``,
with the ``blackSpotId`` and ``blackSpotDistance`` also recorded.


.. _screenIllumination:
Screen illumination
~~~~~~~~~~~~~~~~~~~

The screen illumination correction is only applied to quartz exposures
(i.e., not sky exposures),
with the intent of correcting the quartz spectra to look like they come from the sky.
The correction is:

.. math::

    c_{\rm scr} = a x' y' + b x' + c y' + 1

where :math:`a \sim\ -1.6 \times\ 10^{-7}`,
:math:`b \sim\ -8.0 \times\ 10^{-5}`
and :math:`c \sim\ -1.1 \times 10^{-4}`
are the coefficients;
:math:`x'` and :math:`y'` is the position on the focal plane (in mm)
after correcting for the instrument rotator angle.

.. math::

    x' & = x \cos\theta - y \sin\theta \\
    y' & = x \sin\theta + y \cos\theta

where :math:`x` and :math:`y` are the positions on the focal plane (in mm) from the ``pfsConfig``,
and :math:`\theta` is the instrument rotator angle
(from the ``INSROT`` header keyword).

The screen illumination correction is applied within the ``ReduceExposureTask`` task,
by the ``pfs.drp.stella.screen.ScreenResponseTask``,
if the configuration parameter ``reduceExposure:doApplyScreenResponse=True``.
The ``ScreenResponseTask`` checks that the exposure is a quartz exposure
before applying the correction.


.. _pfiCorrections:
PFI corrections
~~~~~~~~~~~~~~~

Multiple corrections are grouped under the heading of "PFI corrections",
because they are related to the position of the fiber within its patrol region
at the time of the science exposure [#]_ .

.. [#] Probably more accurately, they were discovered around the same time,
       so they were grouped together for convenience.
       Possibly the black spot correction belongs with them too.

Edge vignetting:
the outer half of the patrol region of fibers near the autoguider
(near the center of each hexagon edge)
is vignetted up to 20%.
The current model is a power-law with separate scales parallel and perpendicular to the hexagon edges.
It is not a great fit, but is better than nothing.
The parameters are set in the ``pfs.drp.stella.PfiCorrection.EdgeVignettingConfig``.

Blob vignetting:
a feature on the PFI cover plate near ``fiberId=2518`` results in an area of vignetting up to 30%.
The current model is a 2D elliptical Gaussian
(which looks like a "blob", hence the name).
The fit is not ideal, but it is better than nothing.
The parameters are set in ``drp_pfs_data/pfi/pfi_blob.fits``,
which is read by ``pfs.drp.stella.PfiCorrection.BlobVignetting``.
Although this is expandable,
it currently contains only a single Gaussian that affects only a single fiber.

Fiber throughput variation:
the fiber throughput varies with position within its patrol region,
due to misalignment of the fiber lens with the converging beam
as the cobra moves the lens around the patrol region.
The current model is a 2D polynomial
(``order=6`` in an attempt to fit some sharp features, though not very successfully),
with the parameters set in ``drp_pfs_data/pfi/pfi_fibers.fits``,
which is read by ``pfs.drp.stella.focalPlaneFunction.FiberPolynomials`` as a ``ConstantPerFiber``.
We are eagerly looking forward to a more physically-motivated model that will provide a better fit.

Common mode of the skyNorms:
the mean of the skyNorms over a run [#]_ is stored in the ``skyNorms_calib`` butler product.
One might ask why this is non-zero, since we have previously applied the fiberNorms.
My guess is that this is the difference in normalization between fibers at the ``HOME`` position
(where the `fiberNorms` are taken)
and the "mean" position of the fibers during science exposures.
If we have a good model of the fiber throughput variation over the patrol region,
then we should not need this correction.

.. [#] Or whatever temporal range the Calib Czar chooses to employ.

The "PFI corrections" are applied within the ``ReduceExposureTask``,
by the ``pfs.drp.stella.PfiCorrection.PfiCorrectionTask``,
if the configuration parameter ``reduceExposure:doApplyPfiCorrection=True``.
If ``reduceExposure:doApplySkyNorms=True``,
the common mode correction from the skyModes is also applied.
The total value of the correction for each fiber is written to the ``pfsArm.notes.pfiCorrection``.
Fibers without a finite correction value have their spectra masked with ``BAD_PFI_CORRECTION``.


Application
-----------

When running the ``ReduceExposureTask`` on a science exposure,
the result is that the ``pfsArm.flux`` spectra correspond to the extracted spectra from the image,
and the ``pfsArm.norm`` spectra consist of the contents of the ``fiberNorms_calib``,
with the black spot and PFI corrections (including the skyNorms common mode) applied.

When running the ``ReduceExposureTask`` on a quartz exposure,
the result is that the ``pfsArm.flux`` spectra correspond to the extracted spectra from the image,
and the ``pfsArm.norm`` spectra consist of the contents of the ``fiberNorms_calib``,
with the black spot, screen illumination and PFI corrections (including the skyNorms common mode) applied.
