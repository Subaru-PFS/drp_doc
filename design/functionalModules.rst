.. _functionalModules:

Functional Modules
------------------

Here we describe the individual modules comprising the pipeline:
their inputs, components, algorithms, and outputs.

Top-level modules
*****************

The following top-level modules will be implemented as ``lsst.pipe.base.CmdLineTask``\ s
(possibly with MPI for scatter-gather operations).
They may be run independently, or by a master pipeline driver script
(which could be a ``lsst.ctrl.pool.BatchPoolTask`` or its successor).


.. _constructBias:

_constructBias
^^^^^^^^^^^^^^

``constructBias`` operates on a set of bias exposures of a single spectrograph arm.
For each input image, we apply the usual instrument signature removal (ISR) steps
up to and not including bias subtraction.
Then we average the individual exposures,
with a mild clipping to reject deviant pixels.
The final product is the combined master bias.

* Input datasets:

  + ``raw``: exposures to combine.

* Output datasets:

  + ``bias``: master bias; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _constructDark:

_constructDark
^^^^^^^^^^^^^^

``constructDark`` operates on a set of dark exposures of a single spectrograph arm.
For each input image, we apply the usual instrument signature removal (ISR) steps
up to and not including dark subtraction,
and mask cosmic-rays on the basis of their morphology.
Then we average the individual exposures,
with clipping to reject deviant pixels.
The final product is the combined master dark.

* Input datasets:

  + ``raw``: exposures to combine.

* Output datasets:

  + ``dark``: master dark; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _constructFiberFlat:

constructFiberFlat
^^^^^^^^^^^^^^^^^^

``constructFiberFlat`` operates on a set of quartz exposures of a single spectrograph arm,
where the slit position has been dithered along the slit dimension.
It can operate separately on individual spectrograph arms:
there is no need to coordinate the operations for different arms or spectrographs,
because this is solely a calibration of individual detectors
and no flux calibration is taking place [#]_.

.. [#] A relative flux calibration occurs in constructFiberTrace.
       It would be difficult to do a flux calibration here,
       because the wings of the fibers overlap,
       so that a single pixel can contain flux from two fibers;
       therefore merely scaling the pixel values in the flat cannot flux-calibrate a single fiber.

For each input image, we apply the usual instrument signature removal (ISR) steps
up to and not including flat-fielding,
and mask cosmic-rays on the basis of their morphology.
Then we combine the individual images,
normalizing the pixels within the row of each fiber by the total flux in that fiber row:

.. math::
   F(i, x, y) = \sum_j f_j(i, x, y) / \sum_x f_j(i, x, y)

where :math:`F(i, x, y)` is the combined flat-field
with the flux in fiber :math:`i` as a function of position, :math:`(x, y)`;
and :math:`f_j(i, x, y)` is the :math:`j`-th input image.

The final product is the combined master flat image.

* Input datasets:

  + ``raw``: exposures to combine.
  + ``bias``, ``dark``: master bias and dark for ISR.
  + ``detectorMap``: map of fiber positions, may be used for finding fibers.

* Output datasets:

  + ``flat``: master flat; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _constructFiberTrace:

constructFiberTrace
^^^^^^^^^^^^^^^^^^^

``constructFiberTrace`` operates on a set of quartz exposures of a single spectrograph arm,
where the slit position is held constant
and different fibers are illuminated in each exposure.
It can operate separately on individual spectrograph arms:
there is no need to coordinate the operations for different arms or spectrographs,
because the quartz illumination of the screen (assumed constant) is sufficient to link them already.

For each input image, we apply the usual instrument signature removal (ISR) steps
and mask cosmic-rays on the basis of their morphology.
Then we find and centroid traces on each image, measure the trace profiles and extract the spectra.
Next, the fiber traces are identified using the detectorMap,
and the sets of fiber traces from the individual images are merged.
Finally, each trace profile is normalized so that the extracted spectrum would match some reference spectrum:

.. math::
   t^*(i, \lambda) = t(i, \lambda) * R(\lambda)/S(i, \lambda)

where :math:`t^*(i, \lambda)` is the normalized trace of the :math:`i`-th fiber for wavelength :math:`\lambda`,
:math:`t(i, \lambda)` is the raw trace,
:math:`R(\lambda)` is the reference spectrum,
and :math:`S(i, \lambda)` is the extracted spectrum of the :math:`i`-th fiber.

The reference spectrum is arbitrary,
and can be chosen for convenience or ease of flux calibration [#]_.
Some possibilities are:

* A smoothed version of the median extracted spectrum.
* A flat spectrum of unit value.
* A 4500 K black body.

.. [#] The reference spectrum should be smooth
       over the wavelength scale corresponding to any wavelength calibration errors.

The final product is the normalized fiber trace.

* Input datasets:

  + ``raw``: exposures to use.
  + ``bias``, ``dark``, ``flat``: master bias, dark and flat for ISR.
  + ``detectorMap``: map of fiber positions, used for finding fibers and rough wavelength calibration.

* Output datasets:

  + ``fiberTrace``: trace of fibers; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _constructDetectorMap:

constructDetectorMap
^^^^^^^^^^^^^^^^^^^^

``constructDetectorMap`` operates on a set of arc exposures of a single spectrograph arm,
where the slit position is held constant while different arc lamps are exposed in turn.
It can operate separately on individual spectrograph arms, as each can be calibrated separately.

For each input image, we apply the usual instrument signature removal (ISR) steps
and mask cosmic-rays on the basis of their morphology
before extracting spectra for each fiber.
Arc lines are identified in each fiber's spectrum,
and the lines are centroided.
For each fiber, the list of arc lines and their centroids for each input image is collected,
and the wavelength solution is fit [#]_;
this solution is used to update the detectorMap.

.. [#] It's best to fit a function to the residuals of the wavelength solution provided by the detectorMap.

This updated detectorMap is the final product.

* Input datasets:

  + ``raw``: exposures to use.
  + ``bias``, ``dark``, ``flat``: master bias, dark and flat for ISR.
  + ``fiberTrace``: for extracting spectra.
  + ``bootstrapDetectorMap``: a theoretical or average detectorMap for bootstrapping the specific detectorMap we're constructing.

* Output datasets:

  + ``detectorMap``: map of fiber positions and wavelengths; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _constructPsf:

constructPsf
^^^^^^^^^^^^

``constructPsf`` operates on a set of raw out-of-focus ("donut") arc exposures.
It operates separately on individual spectrograph arms,
as the camera in each arm is independent.

For each input image, we apply the usual instrument signature removal (ISR) steps
and mask cosmic-rays on the basis of their morphology.
Then, *with some sort of dark magic that I don't understand,*
the donuts are fit with the model PSF.

The final product is the PSF model parameters.

* Input datasets:

  + ``raw``: exposures to use.
  + ``bias``, ``dark``, ``flat``: master bias, dark and flat for ISR.
  + ``detectorMap``: map of fiber position and wavelength, for identifying fibers and arc lines.

* Output datasets:

  + ``psfParams``: PSF parameters; primary product.
  + ``postISRCCD``: cached ISR-corrected exposures.


.. _reduceExposure:

reduceExposure
^^^^^^^^^^^^^^

``reduceExposure`` operates on a set of raw science exposures
for all arms of the same kind over the entire instrument,
as it needs to fit models as a function of wavelength over the entire field of view
in the two-dimensional sky subtraction.

For each input image, we apply the usual instrument signature removal (ISR) steps
and mask cosmic-rays on the basis of their morphology.
Then, if it found to be necessary, we can tweak the wavelength solution in the detectorMap
by extracting the spectra and fitting the wavelengths of the sky lines.

Next we perform the two-dimensional sky subtraction (see subtractSky2d_ for details).
Finally, for each arm the spectra are extracted and written as the final product.

* Input datasets:

  + ``raw``: exposures to use.
  + ``bias``, ``dark``, ``flat``: master bias, dark and flat for ISR.
  + ``psfParams``: PSF parameters, for subtractSky2d_.
  + ``fiberTrace``: fiber profiles for extraction.
  + ``detectorMap``: map of fiber position and wavelength, for wavelength calibration.
  + ``pfiConfig``: top-end configuration, for identifying sky fibers.

* Output datasets:

  + ``pfsArm``: sky-subtracted, wavelength-calibrated spectra from arm; primary product.
  + ``postISRCCD``: ISR-corrected exposure.
  + ``psf``: PSF model, from subtractSky2d_.
  + ``sky2d``: 2d sky model, from subtractSky2d_.
  + ``lsf``: line-spread function, from subtractSky2d_.


.. _mergeArms:

mergeArms
^^^^^^^^^

``mergeArms`` operates on all arms for the entire instrument,
as it needs to fit models as a function of wavelength over the entire field of view
in the one-dimensional sky subtraction,
and it merges the arms within each spectrograph.

For all arms of the same kind,
we perform a one-dimensional sky subtraction (see subtractSky1d_ for details).
Now that we are done with corrections in the frame of the instrument,
we can apply a barycentric wavelength correction.
Finally, the spectra from the arms of each spectrograph are merged.
The final product is the merged, sky-subtracted, wavelength-calibrated and barycentric-corrected spectra
for the entire field of view.

* Input datasets:

  + ``pfsArm``: sky-subtracted, wavelength-calibrated spectra from arm.
  + ``lsf``: line-spread function.
  + ``pfiConfig``: top-end configuration, for identifying sky fibers.

* Output datasets:

  + ``pfsMerged``: Merged spectra for all spectrographs+arms; primary product.
  + ``sky1d``: 1d sky model, from subtractSky1d_.

* Algorithmic details:

  + We might do the merge using the `Kirkby-Kaiser algorithm`_.

.. _Kirkby-Kaiser algorithm: https://github.com/dkirkby/baad


.. _calculateReferenceFlux:

calculateReferenceFlux
^^^^^^^^^^^^^^^^^^^^^^

``calculateReferenceFlux`` operates on spectra from the entire field-of-view
(i.e., the output of mergeArms_).

For each spectrum that will be used for flux calibration (typically F-stars),
we determine the most suitable reference spectrum from a grid of models.
This reference spectrum should be scaled to the correct flux
using broad-band photometry from the ``pfiConfig``.
The final product is the flux-corrected reference spectra.

* Input datasets:

  + ``pfsMerged``: Merged spectra for all spectrographs+arms.
  + ``pfiConfig``: top-end configuration, for identifying calibration fibers.
  + ``refModels``: grid of reference models.

* Output datasets:

  + ``pfsReference``: reference spectra; primary product.


.. _fluxCalibrate:

fluxCalibrate
^^^^^^^^^^^^^

``fluxCalibrate`` operates on spectra from the entire field-of-view
(i.e., the output of mergeArms_).

For each spectrum that will be used for flux calibration (typically F-stars)
we measure the flux calibration vector.
We model the ensemble of flux calibration vectors over the focal plane,
and apply the flux calibration model to the science spectra.
Finally, the science spectra can be tweaked
to match the broad-band photometry in the ``pfiConfig``.
The final product is the wavelength-calibrated, flux-calibrated spectra for the entire field of view.

* Input datasets:

  + ``pfsMerged``: Merged spectra for all spectrographs+arms.
  + ``pfiConfig``: top-end configuration, for identifying calibration fibers.
  + ``pfsReference``: reference spectra.

* Output datasets:

  + ``pfsObject``: flux-calibrated object spectra; primary product.
  + ``fluxCal``: flux calibration parameters.

* Algorithmic details:

  + When modeling the flux calibration over the field of view,
    we could consider weighting by the distance of the fiber position from the nominal position.


.. _coaddSpectra:

coaddSpectra
^^^^^^^^^^^^

``coaddSpectra`` operates on a set of spectra from the entire field-of-view.

First, we read the input ``pfiConfig`` files to determine the list of objects and their inputs,
and then we coadd the input spectra of each object.
In order to construct a coadd without correlated noise,
we need to go back to the original extracted spectra (before merging arms).
This requires re-applying the calibrations that were originally calculated from the merged spectra,
specifically, the one-dimensional sky subtraction and flux calibration.

* Input datasets:

  + ``pfiConfig``: top-end configuration, for identifying calibration fibers.
  + ``pfsArm``: sky-subtracted, wavelength-calibrated spectra from arm.
  + ``sky1d``: 1d sky model, from subtractSky1d_.
  + ``fluxCal``: flux calibration parameters, from fluxCalibrate_.

* Output datasets:

  + ``pfsCoadd``: coadded spectrum; primary product.

* Algorithmic details:

  + We coadd the original (un-resampled) spectra using the `Kirkby-Kaiser algorithm`_.

.. _Kirkby-Kaiser algorithm: https://github.com/dkirkby/baad


Lower-level modules
*******************

The following modules support the top-level modules:
they do not need to be stand-alone executables.
They will be implemented as ``lsst.pipe.base.Task``\ s
that return ``lsst.pipe.base.Struct``\ s with the necessary outputs.
Multiple versions of these modules may be developed with increasingly sophisticated algorithms
as the pipeline grows in functionality.


.. _subtractSky2d:

subtractSky2d
^^^^^^^^^^^^^

``subtractSky2d`` subtracts sky lines from the two-dimensional images
(i.e., before extracting the spectra).
This is important because the sky lines from neighboring fibers overlap,
especially when the lines are bright.

This module operates on all arms of the same kind for the entire instrument
in a single exposure
(e.g., all red arms in a single exposure).
This is necessary because we will fit models as a function of wavelength over the entire field of view.

This module requires the following inputs:

* ``exposureList`` (``list`` of ``lsst.afw.image.Exposure``):
  a list of exposures for the arms;
  these shall be modified (the sky shall be subtracted).
* ``pfiConfig`` (``pfs.datamodel.PfiConfig``): configuration of the top-end, for identifying sky fibers.
* ``fiberTraceList`` (``list`` of ``pfs.drp.stella.FiberTraceSet``):
  a list of fiber traces for the arms
  (same order as for ``exposureList``).
* ``detectorMapList`` (``list`` of ``pfs.drp.stella.DetectorMap``):
  a list of detectorMaps for the arms
  (same order as for ``exposureList``).
* ``psfParamsList`` (``list`` of ``pfs.drp.stella.PfsPsfParams``):
  a list of PSF parameters for the arms
  (same order as for ``exposureList``).
* ``skyLineList`` (``list`` of ``pfs.drp.stella.ReferenceLine``):
  a list of sky lines.

We will first remove the sky continuum so that we can measure the sky lines.
In order to do so, we will extract the spectra
and fit a continuum to the sky fibers.
This continuum can be modelled as a function of RA,Dec (fitFocalPlane_),
and it is then subtracted from all fibers in two dimensions
(using the fiber profiles in the ``fiberTraceList`` to construct images with the sky continuum spectra).

Next, we measure the sky lines.
The details of this step have not been worked out yet,
but it likely involves fitting a PSF (using the provided ``psfParamsList``),
fitting the PSF to the sky lines to measure their intensity,
modelling the intensity as a function of focal plane position (fitFocalPlane_),
and then generating model images (using the PSF and sky line model)
which can be subtracted from the input images.

The outputs of this module shall be:

* ``psfList`` (``list`` of ``pfs.drp.stella.PfsPsf``):
  the fit PSFs
  (same order as for ``exposureList``).
* ``continuumModel`` (class TBD):
  the model for the sky continuum.
* ``skyLineModel`` (class TBD):
  the model for the sky lines.


.. _subtractSky1d:

subtractSky1d
^^^^^^^^^^^^^

``subtractSky1d`` subtracts the sky from the one-dimensional spectra.
This can be used to clean up the residuals after two-dimensional sky subtraction (subtractSky2d_),
or as the primary sky-subtraction technique.

This module requires the following inputs:

* ``spectraList`` (``list`` of ``pfs.drp.stella.SpectrumSet``):
  a list of spectra for the arms;
  these shall be modified (the sky shall be subtracted).
* ``pfiConfig`` (``pfs.datamodel.PfiConfig``):
  configuration of the top-end, for identifying sky fibers.
* ``lsfList`` (``list`` of ``pfs.drp.stella.Lsf``):
  a list of line-spread functions for the arms
  (same order as for ``exposureList``).
* ``skyLineList`` (``list`` of ``pfs.drp.stella.ReferenceLine``):
  a list of sky lines.

This module consists of four parts:

#. Use the sky fibers to generate a model for the sky.
   Multiple models can be imagined for this:

   * A multiple of the average sky spectrum.
   * A linear combination of principal components.
   * A continuum plus discrete sky lines.

#. Fit the model to the sky fibers.
#. Fit the model parameters as a function of position on the focal plane (fitFocalPlane_).
#. Subtract the model from all the fibers.

The outputs of this module shall be:

* ``skyModel`` (class TBD):
  the model for the sky.


.. _fitFocalPlane:

fitFocalPlane
^^^^^^^^^^^^^

``fitFocalPlane`` fits a set of vectors for fibers over the focal plane.
These vectors might be a spectrum for each fiber,
or the parameters of a model,
but each needs to be modelled as a function of position on the focal plane.

This module requires the following inputs:

* ``vectorList`` (``list`` of ``numpy.ndarray``):
  Vectors to model over the focal plane.
* ``fiberIdList`` (``list`` of ``int``):
  List of corresponding fiber IDs
  (same order as ``vectorList``).
* ``pfiConfig`` (``pfs.datamodel.PfiConfig``):
  configuration of the top-end,
  for mapping fiber ID to focal-plane position.
* ``evalFiberIdList`` (``list`` of ``int``):
  List of fiber IDs for which the model should be evaluated;
  may be ``None`` to indicate that the model should be evaluated for all fibers in the ``pfiConfig``.

In addition to these inputs,
a set of configuration parameters will govern how the fit is done:

* ``raOrder`` (``int``):
  Polynomial order in RA.
* ``decOrder`` (``int``):
  Polynomial order in Dec.
* ``rejIter`` (``int``):
  Number of rejection iterations.
* ``rejThreshold`` (``float``):
  Rejection threshold (standard deviations).
* ``weighting`` (``str``):
  Specifies how weighting is to be done:

  + ``uniform``: no weighting.
  + ``offset``: weight by distance between actual fiber position and nominal fiber position.


This should be a simple matter of fitting a two-dimensional polynomial,
with optional rejection and weighting.
Each vector index is fit independently.

The outputs of this module shall be:

* ``modelList`` (``list`` of some polynomial class):
  Polynomial fit for each vector index
  (same order as ``vectorList``).
* ``chi2List`` (``list`` of ``float``):
  The :math:`\chi^2` value for each fit
  (same order as ``vectorList``).
* ``numList`` (``list`` of ``int``):
  The number of values used for each fit
  (same order as ``vectorList``).
* ``evalList`` (``list`` of ``numpy.ndarray``):
  The evaluated vectors for each of the fibers in the ``evalFiberIdList``
  (same order as ``evalFiberIdList``,
  or if ``evalFiberIdList`` is ``None`` then the same order as in the ``pfiConfig``).


.. _extractSpectra:

extractSpectra
^^^^^^^^^^^^^^

``extractSpectra`` extracts spectra from an image,
given the fiber traces and detectorMap.

The module requires the following inputs:

* ``image`` (``lsst.afw.image.MaskedImage``):
  Image from which to extract spectra.
* ``traces`` (``pfs.drp.stella.FiberTraceSet``):
  Fiber traces, specifying the position and profile as a function of row.
* ``detectorMap`` (``pfs.drp.stella.DetectorMap``):
  Map of fiber position and wavelength on the detector;
  used for the wavelength solution.

The extraction could be done with one of a number of algorithms,
the choice of which will be set by a configuration parameter:

#. Boxcar extraction:
   sum the data in pixels around the peak.
   This is the simplest possible algorithm, but doesn't maximize signal-to-noise;
   useful for testing.
#. "Optimal extraction":
   sum the data weighted by the fiber profile.
   This is a better algorithm for optimising the signal-to-noise,
   but it doesn't deal with neighboring fibers which may contaminate the fiber being extracted.
#. Simultaneous fit:
   solve the tri-diagonal matrix from least-squares fitting a linear combination of fiber profiles.
   This can be done in linear time, so it should be fast enough.
   This approach deals with neighbors, and is likely the ultimate algorithm we will use for science.
#. Iterative extractions:
   one can imagine an iterative approach whereby the optimal extraction is performed iteratively.
   We don't expect to use this algorithm.

These will be coded in C++ (as a method of the ``FiberTrace`` class) for speed.

The outputs of this module shall be:

* ``spectra`` (``pfs.drp.stella.SpectrumSet``):
  The extracted spectra.

