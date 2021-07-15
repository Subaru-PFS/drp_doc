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

