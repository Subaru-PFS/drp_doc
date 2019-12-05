.. _datasets:

Datasets
--------

Here we describe the various products of the pipeline.
Some are intended for internal use,
while others are intended for science users.


Raw products
^^^^^^^^^^^^

The following products are provided by the observing system,
and ingested into the data repository as the first step in pipeline operations:

* ``raw`` (``lsst.afw.image.ImageU``):
  the raw image from the data acquisition system.
* ``pfiConfig`` (``pfs.datamodel.PfsConfig``):
  top-end configuration, for mapping fibers to their targets.


Calib products
^^^^^^^^^^^^^^

* ``bias`` (``lsst.afw.image.Exposure``):
  master bias frame.
* ``dark`` (``lsst.afw.image.Exposure``):
  master dark frame.
* ``flat`` (``lsst.afw.image.Exposure``):
  mask flat frame,
  constructed from dithered quartz exposures.
* ``fiberTrace`` (``pfs.drp.stella.FiberTraceSet``):
  position and profile of each fiber as a function of row.
* ``detectorMap`` (``pfs.drp.stella.DetectorMap``):
  mapping between fiber and wavelength to position on the detector.
* ``bootstrapDetectorMap`` (``pfs.drp.stella.DetectorMap``):
  a theoretical or average detectorMap for bootstrapping the specific detectorMap we're constructing.
* ``psfParams`` (type TBD):
  PSF parameters, determined from donut exposures.


Reference products
^^^^^^^^^^^^^^^^^^

The following products provide bulk data for the operation of pipeline algorithms.
They may be provided by the butler, or some other mechanism
(e.g., files or directories in ``obs_pfs``, a ``git-lfs`` repo, etc.).

* ``refModels`` (type TBD):
  a grid of reference models, used for :ref:`calculateReferenceFlux`.
* ``arcLines`` (type TBD):
  a list of arc lines:
  their wavelengths, identifications, strengths and flags indicating whether they should be used or not.
* ``skyLines`` (type TBD):
  a list of sky lines:
  their wavelengths, identifications, strengths and flags indicating whether they are resolved or not.


Temporary products
^^^^^^^^^^^^^^^^^^

The following products are produced for convenience only,
and can in general be deleted once their usefulness has been realised:

* ``postISRCCD`` (``lsst.afw.image.Exposure``):
  cached ISR-corrected exposure, for calib construction.


Operational products
^^^^^^^^^^^^^^^^^^^^

The following products are produced by the pipeline in the course of operations,
and may be useful for debugging or close inspection of data quality:

* ``psf`` (type TBD):
  PSF model, from :ref:`subtractSky2d`.
* ``sky2d`` (type TBD):
  sky model, from :ref:`subtractSky2d`.
* ``lsf`` (``pfs.drp.stella.LineSpreadFunction``):
  line-spread function, derived from the PSF model, from :ref:`reduceExposure`.
* ``sky1d`` (type TBD):
  sky model, from :ref:`subtractSky1d`.
* ``fluxCal`` (type TBD):
  flux calibration, from :ref:`fluxCalibrate`.
* ``pfsReference`` (``pfs.datamodel.PfsSpectra``):
  reference spectra, from :ref:`calculateReferenceFlux`.
* ``pfsMerged`` (``pfs.datamodel.PfsSpectra``):
  arm-merged spectra for the entire instrument,
  from :ref:`mergeArms`.


Science products
^^^^^^^^^^^^^^^^

These are the main science products of the pipeline.

* ``pfsArm`` (``pfs.datamodel.PfsSpectra``):
  sky-subtracted, wavelength-calibrated spectra from a single arm of a single spectrograph,
  from :ref:`reduceExposure`.
  Since these spectra have not been resampled after extraction,
  this may be useful for identifying cosmic-ray hits masquerading as emission lines in the ``pfsSingle`` or ``pfsObject``.
* ``pfsSingle`` (``pfs.datamodel.PfsSingle``):
  flux-calibrated, barycentric wavelength-calibrated object spectrum from a single exposure,
  from :ref:`fluxCalibrate`.
  This is useful for investigating variations from exposure to exposure,
  or identifying cosmic-ray hits masquerading as emission lines in the ``pfsObject``.
* ``pfsObject`` (``pfs.datamodel.PfsSingle``):
  coadded spectrum from multiple exposures,
  from :ref:`coaddSpectra`.
  This is the main science product that most science users will want.
