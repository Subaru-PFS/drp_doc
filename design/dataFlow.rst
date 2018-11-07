.. _dataFlow:

Pipeline Data Flow
------------------

Here we outline a general overview of the pipeline,
tracing the flow of data through the pipeline from raw data to the delivered product.
We will introduce the major components,
but a detailed explanation of the subcomponents is deferred to the section on :ref:`functionalModules`.

Data Repository
^^^^^^^^^^^^^^^

The LSST stack includes an I/O abstraction layer known as the "data butler", or just "the butler".
The butler maps keyword-value pairs into file paths within the "data repository" using pre-defined templates.
In order to access raw data, it must first be ingested into the data repository.
The LSST stack provides a script to perform this, which we will use: ``ingestImages.py`` [#]_.

.. [#] As of Novemeber 2018, this script ingests only raw images.
   We will need to modify it to also ingest the ``pfiConfig`` files.

Example usage::

  imagestImages.py /path/to/repo /path/to/raw/data/*.fits


Within a data repository, outputs are typically written within a "rerun" directory
specified by a symbolic name (usually with the ``--rerun`` command-line argument).
This serves to group products from a processing run together.


Calib Construction
^^^^^^^^^^^^^^^^^^

"Calibs" are versioned calibration products wherein
the behavior of the instrument is modeled (often using dedicated observations) and recorded
for use in removing the instrumental signature of science data.
The flow of the calib construction is shown in :numref:`pfsCalibs`.

.. _pfsCalibs:

.. figure:: pfsCalibs.pdf

   **The calib construction components of the pipeline.**
   Each component on the left constructs the products on the right,
   which are used for subsequent components.

The LSST stack includes a facility for constructing calibs
and ingesting them into a calibration repository for later retrieval [#]_.
We will use the LSST scripts for constructing biases and darks,
as these are constructed in the same way for spectroscopy as for imaging;
and we will also use the LSST script for ingesting the calibs into the calibration repository.

.. [#] The current calib system is crude, having grown organically, but it should serve our purposes.
       We expect it will mature over the next few years as the LSST team devotes more attention to it.

Example construction of a bias calib::

  constructBias.py /path/to/repo --calib /path/to/calibs --rerun calib/bias --id object=BIAS dateObs=2018-11-06 <operational arguments>
  ingestCalibs.py /path/to/repo/ --calib /path/to/calibs /path/to/repo/rerun/calib/bias/.../*.fits --validity 30

Example construction of a dark calib::

  constructDark.py /path/to/repo --calib /path/to/calibs --rerun calib/dark --id object=DARK dateObs=2018-11-06 <operational arguments>
  ingestCalibs.py /path/to/repo --calib /path/to/calibs /path/to/repo/rerun/calib/dark/.../*.fits --validity 30

At this point, we need to use our own calib construction modules,
as our spectroscopic flat fields are observed and combined differently than for imaging.
The inputs for our flat field construction script are quartz lamp observations
with the slit position dithered in the dimension of the slit (i.e., ``x`` offsets).
A new script, ``constructFiberFlat.py`` (see :ref:`constructFiberFlat`), will combine these::

  constructFiberFlat.py /path/to/repo --calib /path/to/calibs --rerun calib/flat --id object=QUARTZ dateObs=2018-11-06 <operational arguments>
  ingestCalibs.py /path/to/repo --calib /path/to/calibs /path/to/repo/rerun/calib/flat/.../*.fits --validity 1000

Next, we need to map the precise location and profile of each fiber's trace on the detector
(see :ref:`constructFiberTrace`).
It's possible [#]_ that this will have to be done independently for each science observation
since the location and profile can have subtle changes with changes in the cobra position.
Currently there is no simple way of associating fiber traces with individual science exposures
(as opposed to associating a fiber trace with all science exposures in some validity range),
but it should be simple to modify the LSST calibs system to do this if the need arises.
Furthermore, when the slit is fully populated the fiber profiles will overlap,
and we will need to use two input exposures:
one for the odd fibers and one for the even fibers.
Because the fiber traces are obtained by all fibers observing the same quartz lamp,
this also provides an opportunity to provide a relative flux calibration across all the fibers.
Here is an example::

  constructFiberTrace.py /path/to/repo --calib /path/to/calibs --rerun calib/fiberTrace --id visit=123^124 <operational arguments>
  ingestCalibs.py /path/to/repo --calib /path/to/calibs /path/to/repo/rerun/calib/fiberTrace/.../*.fits --validity 1

.. [#] Perhaps even likely.

We now need to map the wavelength solution over the detectors
(see :ref:`constructDetectorMap`).
Similar to the case for the fiber traces,
this may need to be done independently for each science observation,
but for now we will assume not.
Here is an example::

  constructDetectorMap.py /path/to/repo --calib /path/to/calibs --rerun calib/detectorMap --id object=ARC dateObs=2018-11-06 <operational arguments>
  ingestCalibs.py /path/to/repo --calib /path/to/calibs /path/to/repo/rerun/calib/detectorMap/.../*.fits --validity 1

Finally, we need the PSF model parameters (see :ref:`constructPsf`).
The exact contents of these PSF model parameters is yet to be determined,
but it's clear that they are an important input to the pipeline
and they will change with changes to the instrument,
so it makes sense to treat them as a calib.
Here's a possible example::

  constructPsf.py /path/to/repo --calib /path/to/calibs --rerun calib/psf --id object=DONUT dateObs=2018-11-06 <operational arguments>
  ingestCalibs.py /path/to/repo --calib /path/to/calibs /path/to/repo/rerun/calib/psf/.../*.fits --validity 1


Science observations
^^^^^^^^^^^^^^^^^^^^

The flow of science data through the pipeline is shown in :numref:`pfsScience`.

.. _pfsScience:

.. figure:: pfsScience.pdf

   **The components of the pipeline for processing science observations.**

The first operation when processing science observations is the most involved:
the extraction of sky-subtracted spectra.
``reduceExposure.py`` (see :ref:`reduceExposure`) will operate on all arms of the same flavor
(e.g., the blue arms from each spectrograph)
so that the maximum information is available for modeling the sky.
It will first perform the instrument signature removal (ISR),
subtracting the bias and dark, and dividing by the flat.
Then it will fit a PSF model to the sky lines,
model the collection of sky line fluxes over the fibers,
and subtract the sky lines from the images.
Finally, the spectra will be extracted using the fiber trace and detector map.
The product is a collection of sky-subtracted spectra for each spectrograph arm (``pfsArm``).
Each will have been wavelength-calibrated (through the detectorMap, and perhaps tweaks using the sky lines)
and a relative (across arms) flux calibration (through the fiber trace).
Here is an example command-line::

  reduceExposure.py /path/to/repo --calib /path/to/calib --rerun science --id visit=123 arm=r <operational parameters>

Next, we merge the arms within each spectrograph,
so that subsequent operations can be done using all available spectral information for each object.
This also provides an opportunity to clean up any residuals in the 2D sky subtractions
by fitting the sky residuals over the fibers
and subtracting from the extracted spectra.
The result is a set of spectra covering the entire spectral range, for the entire field-of-view.
An example command-line is::

  mergeArms.py /path/to/repo --calib /path/to/calib --rerun science --id visit=123 <operational arguments>

We now turn our attention to flux calibration of the extracted, merged spectra.
The first thing we need to do for this is
generate a set of reference spectra for the calibration
(see :ref:`calculateReferenceFlux`).
An example command-line is::

  calculateReferenceFlux.py /path/to/repo --calib /path/to/calib --rerun science --id visit=123 <operational arguments>


Now we can use the reference spectra to
measure the flux calibration and apply it to the science targets
(see :ref:`fluxCalibrate`).
The result is wavelength-calibrated, flux-calibrated spectra from the visit.
An example command-line is::

  fluxCalibrate.py /path/to/repo --calib /path/to/calib --rerun science --id visit=123 <operational arguments>


The final operation in the pipeline is to coadd spectra of the same object from multiple visits
(see :ref:`coaddSpectra`).
The result is wavelength-calibrated, flux-calibrated coadded spectra.
An example command-line is::

  coaddSpectra.py /path/to/repo --calib /path/to/calib --rerun science --id visit=123^234^345 <operational arguments>
