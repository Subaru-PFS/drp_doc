.. _calibs:

Calibrations
============

"Calibs" are versioned calibration products wherein
the behavior of the instrument is modeled (often using dedicated observations) and recorded
for use in removing the instrumental signature of science data.
The design for the flow of the calib construction pipeline is shown in :numref:`pfsCalibs`.

.. note:: This diagram represents the intended design rather than the actual current state.
          The ``constructDetectorMap`` module is currently named ``reduceArc``,
          and the ``constructPsf`` module does not exist.

.. _pfsCalibs:

.. figure:: pfsCalibs.pdf

   **The calib construction components of the pipeline design.**
   Each component on the left constructs the products on the right,
   which are used for subsequent components.
   Note: this is the intended design, not the current state.

Calibs are created in the following order:

1. Bias
2. Dark
3. Flat
4. Fiber profiles
5. Wavelength solution

Once the pipeline evolves further,
there will likely be additional calibs to be constructed,
such as the PSF parameters.

After each calib is constructed,
it needs to be ingested into the calib repository for use.
This involves specifying a validity range (in days),
which is the time before and after the epoch of the calib that it will be used.
The calib repository can live anywhere, but we normally put it inside the data repository.

The construction of bias, dark, flat and fiber profiles uses an MPI process pool,
so can operate on a cluster over multiple nodes (via Slurm or PBS);
however, the current small data volumes mean this is not helpful at the moment.


Preparation
-----------

Before constructing calibs, make the calib repository::

    mkdir -p /path/to/calibRepo

Next, we ingest some model detector maps [#]_ into the calib repository.
This will be used to identify the fibers being used,
and bootstrap the wavelength solution::

    ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo $DRP_PFS_DATA_DIR/detectorMap/detectorMap-sim-*.fits --mode=copy --validity 1000

.. [#] These particular detector maps were constructed from the instrument simulator
       and so will not have good wavelength solutions for real data until they are updated.
       See `calibsFromScratch`_ for details.


Bias
----

The "bias" is the response of the detector to an exposure of zero length.
The inputs are zero-length exposures, usually designated as ``BIAS``.
Bias calibs are constructed using ``constructPfsBias.py`` [#]_::


  constructPfsBias.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/bias --id field=BIAS
  ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/BIAS/*.fits --validity 1000

.. [#] This is an MPI-based script; use ``--cores`` instead of ``-j`` for parallelism.

Note that here we select the inputs by ``field`` instead of by ``visit`` numbers;
but any method that selects the correct exposures is sufficient.
We use a very long validity range because we assume that the calibrations will be stable [#]_,
and we want to use these calibrations for all data we process.

.. [#] Of course, this needs to be verified.
       Also, some shortcomings in the calibs handling in the LSST butler need to be fixed.

.. note:: The ``r`` and ``m``` arms use the same detectors (with a different grating).
          The ``ingestPfsCalibs.py`` command will automatically generate ``m`` biases
          from ``r`` biases, and vice-versa.


Dark
----

The "dark" is the response of the detector to unit exposure time, with the shutter closed.
The inputs are long exposures taken with the shutter closed, usually designated as ``DARK``.
Dark calibs are constructed using ``constructPfsDark.py`` [#]_::

  constructPfsDark.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/dark --id field=DARK
  ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/DARK/*.fits --validity 1000

.. [#] This is an MPI-based script; use ``--cores`` instead of ``-j`` for parallelism.

.. note:: The ``r`` and ``m`` arms use the same detectors (with a different grating).
          The ``ingestPfsCalibs.py`` command will automatically generate ``m`` darks
          from ``r`` darks, and vice-versa.


Flat
----

The "flat" is the response of the detector to a uniform light source.
For fiber spectroscopy, we don't have a uniform light source with which to illuminate the detector,
so instead we dither the slit head in a direction parallel to the slit head
(i.e., the spatial dimension),
filling in the gaps between the spectra.
The inputs are quartz lamp observations with multiple slit positions.
Flat calibs are constructed using ``constructFiberFlat.py`` [#]_::

  constructFiberFlat.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/flat --id field=QUARTZ
  ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/FLAT/*.fits --validity 1000

.. [#] This is an MPI-based script; use ``--cores`` instead of ``-j`` for parallelism.

.. note:: The ``r`` and ``m`` arms use the same detectors (with a different grating).
          The ``ingestPfsCalibs.py`` command will automatically generate ``m`` flats
          from ``r`` flats, and vice-versa.
          This may be the wrong thing to do with flats, due to wavelength differences.

Fiber profiles
--------------

The "fiber profiles" specifies the profile of each fiber in the spatial dimension.
The input is a quartz lamp observation
with the slit at the same position as will be used for science observations [#]_.
Fiber traces are constructed using ``constructFiberProfiles.py`` [#]_::

  constructFiberProfiles.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/fiberTrace --id field=QUARTZ slitOffset=0.0
  ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/FIBERPROFILES/*.fits --validity 1000

.. [#] It's possible this will have to be done independently for each science observation
       since the location and profile can have subtle changes with changes in the cobra position.
       Also, when the slit is fully populated the fiber profiles will overlap,
       and we will need to use two input exposures:
       one for the odd fibers and one for the even fibers.
       At the moment, we aren't dealing with these details,
       as our current slit head is not fully populated
       and we aren't feeding them through cobras.
.. [#] This is an MPI-based script; use ``--cores`` instead of ``-j`` for parallelism.


Wavelength solution
-------------------

The "detector map" provides a mapping from fiber and wavelength to position on the detector,
essentially a wavelength solution [#]_.
The input is one or more arc observations
with the slit at the same position as will be used for science observations [#]_.
Wavelength solutions are constructed using ``reduceArc.py`` [#]_::

    reduceArc.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/arc --id field=ARC
    ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/arc/DETECTORMAP/*.fits  --validity 1000

.. [#] The ``DetectorMap`` is more than just a wavelength solution,
       but currently this is its primary purpose.
.. [#] Like the fiber profiles, it's possible this will have to be done independently for each science
       observation, since the line centroid might have subtle changes with changes in the cobra position.
       At the moment, we aren't dealing with these details,
       since we aren't using cobras.
.. [#] This is a regular script; use ``-j`` for parallelism.


.. _calibsFromScratch:

Building calibs from scratch
----------------------------

When working with real data (e.g., from Subaru or LAM),
the fiber positions and wavelengths will be slightly offset
from the model detector map predictions based on the simulator.
In that case, a more complicated process than the above linear progression
is required in order to produce a detector map suitable for pipeline operations:


Bootstrap detector map
^^^^^^^^^^^^^^^^^^^^^^

``bootstrapDetectorMap.py`` is used to transform
the detector map from the simulator into something approaching the actual detector map.
It serves to get line position predictions "close enough"
so that ``reduceArc.py`` can reliably centroid the correct line
(so aiming for RMS centroid predictions typically less than a pixel).
The inputs are one quartz exposure (to determine the fiber positions)
and one arc exposure (to determine the wavelength solution)
per arm::

    bootstrapDetectorMap.py /path/to/dataRepo --calib /path/to/calibRepo --rerun calib/bootstrap --flatId visit=123 --arcId visit=456

Because we don't yet have a good detectorMap that will give us robust line identifications
(which is the very reason we're doing this),
``bootstrapDetectorMap.py`` can sometimes have difficulty locking on to a good solution.
While you can ignore warnings about the misidentification of fibers
(which occurs because the fibers are not where they should be, as expected),
you should ensure the *number* of traces matches what is expected,
and check that
the number of lines matched,
the median difference from the detectorMap,
the fit number of points,
and the RMS values
are reasonable.
For example, here is the log output from a good fit to an ``m`` arm with SuNSS data
(251 good fibers, dome lamps)::

    bootstrap.readLineList INFO: Filtered line lists for lamps: ArI,HgI,KrI
    bootstrap INFO: Found 6748 lines in 251 traces
    bootstrap INFO: Matched 6741 lines
    bootstrap INFO: Median difference from detectorMap: 6.389995,4.018591 pixels
    bootstrap INFO: Fit 2983/3309 points, rms: x=0.056048 y=0.173571 total=0.126654 pixels
    bootstrap INFO: Updating detectorMap...
    bootstrap INFO: Median difference from detectorMap: 5.759607,5.856603 pixels
    bootstrap INFO: Fit 2969/3432 points, rms: x=0.067750 y=0.108061 total=0.075888 pixels
    bootstrap INFO: Updating detectorMap...

Some important configuration values you can try playing with include:

* ``readLineList.lampList`` (list of strings):
  the lamps that were on for the arc exposure.
  The software should identify the lamps automatically,
  but if it gets it wrong, you can override its selection.
  Note that this is a list, so it can't be adjusted on the command-line
  and needs to go into a configuration override file (``--config-file``).
* ``spectralOffset`` (float, pixels):
  an offset to apply to the wavelength solution
  before guessing line identifications.
  If you have an approximate guess for the offset
  (e.g., from looking at images with the detectorMap overlaid),
  providing it might help the software guess the right lines.
* ``profiles.profileRadius`` (integer, pixels):
  the radius of the fiber profiles to measure.
  You should set this to half the minimum separation between fibers.
* ``fiberStatus`` (list of ``pfs.datamodel.FiberStatus``):
  list of fiber statuses to allow.
  If you're always finding, e.g., the ``FiberStatus.BROKENFIBER`` fibers,
  include that here.
* ``profiles.findThreshold`` (float, counts):
  the threshold (in the convolved image) for finding fiber traces.
  If there's a lot of scattered light,
  increase this value so you're not picking up noise.

Here's an example of a configuration override file
(supplied to ``bootstrapDetectorMap.py`` with the ``--config-file`` argument)
that was used to produce the above log output::

    config.readLineList.lampList = ["HgI", "KrI", "ArI"]  # otherwise we get sky
    config.spectralOffset = -20  # by-eye estimate
    config.profiles.profileRadius = 3  # because we have some close-packed fibers
    # The following give us only the good fibers, which give us a reliable fiber identification
    from pfs.datamodel import FiberStatus
    config.fiberStatus = [FiberStatus.GOOD]
    config.profiles.findThreshold = 2000  # convolution is probably picking up a lot of scattered light

For further debugging of bootstrap problems,
put the following in a file called ``debug.py`` somewhere on your ``PYTHONPATH``,
and add the ``--debug`` command-line argument to ``bootstrapDetectorMap.py``::

    import lsst.afw.display
    lsst.afw.display.setDefaultBackend("ds9")
    try:
        import lsstDebug
    
        print("Importing debug settings...")
        def DebugInfo(name):
            di = lsstDebug.getInfo(name)
            if name in (
                    "pfs.drp.stella.bootstrap",
            ):
                di.visualize = True  # Display image with detectorMap overlaid?
                di.plotShifts = False  # Quiver plot with shifts?
                di.plotResiduals = True  # Plot fit residuals?
            return di

        lsstDebug.Info = DebugInfo
        lsstDebug.frame = 1
    
    except ImportError:
        import sys
        print("Unable to import lsstDebug; not applying debug settings", file=sys.stderr)

Once you have a decent result, be sure to ingest the detector maps, e.g.::

    ingestPfsCalibs.py /path/to/dataRepo --calib /path/to/calibRepo /path/to/dataRepo/rerun/calib/bootstrap/DETECTORMAP/*.fits  --validity 1000


Iterate with ``constructFiberProfiles.py`` and ``reduceArc.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The quality of the fiber profiles and the quality of the detector map are linked:
the detector map is used to calculate the centers of the fiber traces when measuring the fiber profiles,
and the fiber profiles are used to remove continuum when centroiding arc lines to measure the detector map.
This linkage means that iteration is required to produce good quality calibs when starting from scratch [#]_.

We recommend the following scheme when starting from scratch:

* Bias, dark and flat as usual.
* Bootstrap a detector map.
* Build fiber profiles (``constructFiberProfiles.py``).
* Build wavelength solution (``reduceArc.py``),
  allowing for slit offsets (``--config doSlitOffsets=True``).
* Repeat building of fiber profiles (``constructFiberProfiles.py``).
* Repeat building of wavelength solution (``reduceArc.py``),
  allowing for slit offsets (``--config doSlitOffsets=True``).


.. [#] By "starting from scratch", we mean
       a situation where we have neither
       a good quality ``fiberProfiles``
       nor a good quality ``detectorMap``,
       e.g., when a spectrograph module is first being commissioned.
