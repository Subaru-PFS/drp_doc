Tutorial
--------

This tutorial uses the `integration test`_ as a guide
to the new features and commands of the Gen3-based PFS 2D data reduction pipeline.
The integration test is a script that runs the entire pipeline
on simulated data,
from ingesting raw data,
building calibration products,
and ultimately processing science observations.

.. _integration test: https://github.com/Subaru-PFS/pfs_pipe2d/blob/gen3/bin/pfs_integration_test.sh


Software setup
^^^^^^^^^^^^^^

The Gen3 pipeline requires using a new software stack on the Hilo cluster::

   source /work/stack-2024-07-11/loadLSST.bash
   setup pfs_pipe2d

This new software stack is (currently) based on the LSST stack version 26.0 [#]_.

.. [#] LSST software stack version 27.0 is currently available,
       and we should update the stack version in the future.


Data setup
^^^^^^^^^^

.. note:: Skip over this unless you're running the integration test for yourself.

The integration test uses simulated data contained in the `drp_stella_data package`_,
which must be made available locally.
Some of the headers for the simulated data are not accurate
(but haven't been fixed upstream),
so we need to check and fix them before running the integration test::

    checkPfsRawHeaders.py --fix drp_stella_data/raw/PFFA*.fits
    checkPfsConfigHeaders.py --fix drp_stella_data/raw/pfsConfig-*.fits

These scripts check the headers of the raw data files (``checkPfsRawHeaders.py``)
and the ``pfsConfig`` files (``checkPfsConfigHeaders.py``).
They can be run without the ``--fix`` option to test for errors without fixing them.

.. _drp_stella_data package: https://github.com/Subaru-PFS/drp_stella_data


Repository setup
^^^^^^^^^^^^^^^^

The data repository is a directory that contains the data products
and the configuration files for the Gen3 middleware.
For our tutorial, we'll put the data repository in the ``$DATASTORE`` directory on a local disk,
but the Gen3 middleware includes support for storing data products on remote storage
and various cloud services.

The first step is to create this directory and set up the Gen3 configuration files::

    butler create $DATASTORE --seed-config $OBS_PFS_DIR/gen3/butler.yaml --dimension-config $OBS_PFS_DIR/gen3/dimensions.yaml --override

This specifies two configuration files that are important for the Gen3 middleware.
``butler.yaml`` contains the configuration for the data butler,
specifying the registry and how the pipeline will read and write the various data products.
Most of this can be ignored by the pipeline user,
except for the ``registry`` section,
which specifies the location of the registry database.
The default is to use a SQLite database in the repository directory
(suitable for small-scale testing without extensive parallelization),
but this can be changed to use a PostgreSQL database for better performance.
For example, the following snippet configures the use of the ``drp`` database [#]_::

    registry:
      db: postgresql+psycopg2://pfsa-db:5435/drp

.. [#] Note that in order to use the PostgreSQL database,
       you need to configure the database connection in the ``~/.lsst/db-auth.yaml`` file.

``dimensions.yaml`` contains the configuration for the dimensions of the data products.
Dimensions are a very important concept in the Gen3 middleware,
as they are used to specify data products and
control the parallelization levels of different operations.
Some important dimensions are:

* ``instrument``: the instrument that produced the data.
  The datastore can contain data from multiple instruments,
  but we probably only care about the PFS instrument.
  Usually this will be ``PFS`` for data from Subaru,
  but in the case of the simulated data in the integration test it is ``PFS-F``
  (the ``F`` stands for ``fake``).
* ``exposure``: the exposure number.
  This is the unique identifier for an exposure,
  what we would call a ``visit`` in the Gen2 pipeline.
  In the Gen3 pipeline, ``visit`` is a separate dimension that groups multiple exposures together.
  We may make use of this in the future,
  but for now you should use ``exposure`` (almost) everywhere you used to use ``visit``.
* ``arm``: the spectrograph arm: ``b``, ``r``, ``n``, or ``m``.
* ``spectrograph``: the spectrograph module: 1, 2, 3, or 4.
* ``detector``: the detector number in the camera configuration.
  You shouldn't need to worry about this dimension,
  since it is specified by the combination of ``arm`` and ``spectrograph``.
* ``pfs_design_id``: the unique identifier for the PFS design.
  Notice the spelling (not ``pfsDesignId``), due to the fact that this is a database table name.
* ``dither``: the slit dither.
  This is a new dimension that was not present in the Gen2 pipeline,
  which is used in creating fiber flats.
* ``cat_id``: the unique identifier for the catalog.
  Again, notice the spelling (not ``catId``).
  There is no ``obj_id`` dimension,
  as the large number of objects would overwhelm the database.
* ``skymap``, ``tract``, ``patch``: these specify the sky tessellation.
  They are currently unused in the pipeline,
  but might be used in the future.

Next, we tell the butler about our instrument.
This also copies the camera configuration into the repository::

    butler register-instrument $DATASTORE lsst.obs.pfs.PfsSimulator

The following commands import the defects files
(and any other "curated" calibration files) from the ``drp_pfs_data`` package
(you'll need to be using your own copy of ``drp_pfs_data``, not the shared version)::

    makePfsDefects --lam
    butler write-curated-calibrations $DATASTORE lsst.obs.pfs.PfsSimulator


Data ingestion
^^^^^^^^^^^^^^

Now we can ingest data into the butler repository.
There are two kinds of data that we need to ingest:
raw images and the ``pfsConfig`` files.
These are ingested using two separate commands::

    butler ingest-raws $DATASTORE $drp_stella_data/raw/PFFA*.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
    ingestPfsConfig.py $DATASTORE lsst.obs.pfs.PfsSimulator PFS-F/raw/pfsConfig simulator $drp_stella_data/raw/pfsConfig*.fits --transfer link

The data can be put in the repository in multiple ways,
specified by the ``--transfer`` option,
including ``link``, ``copy``, and ``move`` [#]_.
The ``--fail-fast`` option is useful for debugging,
as it will immediately stop the ingestion process if an error occurs [#]_.

.. [#] See ``lsst.resources.ResourcePath.transfer_from``
       for the full list of transfer options and their meanings.

.. [#] The ``--fail-fast`` option is not useful for bulk ingestion
       of many files, as it will stop the ingestion process after the first error.

The ingestion process places the files
(referred to as "datasets" in the butler)
in the repository and records them in the registry database.
Each file is placed in a "collection",
which can be thought of as a directory in the butler
(and in the case of the datastore on a traditional filesystem,
it is implemented as a directory).
The raw data is placed in the collection ``<instrument>/raw/all``,
while we've specified above that the ``pfsConfig`` files
are placed in the collection ``PFS-F/raw/pfsConfig``.

There are different `kinds of collections`_.
Datasets are always associated with a ``RUN`` collection.
``CALIBRATION`` collections associate datasets with a timespan indicating the validity range.
``CHAINED`` collections provide a search path through multiple collections.

.. _kinds of collections: https://pipelines.lsst.io/modules/lsst.daf.butler/organizing.html#collections

Each dataset is specified by a "dataId",
which is a dictionary of key-value pairs,
where the keys are the dimensions.
For example, a raw image may have a ``dataId`` like
``{'instrument': 'PFS-F', 'exposure': 123, 'arm': 'r', 'spectrograph': 3}``.
A ``pfsConfig`` file is valid for an entire exposure,
so may have a ``dataId`` like
``{'instrument': 'PFS-F', 'exposure': 123}``.

In general, you should treat the files in the datastore as a butler implementation detail,
and use the butler commands and python API to access the data products.
There are some kinds of datastores that do not use a traditional filesystem
(e.g., the S3 datastore),
and so the files may not be directly accessible.

.. warning::
    The registry database tracks all files in the datastore.
    Do not delete files from the datastore without using the appropriate butler commands.

You can see what raw datasets are in the datastore with the following command::

    butler query-datasets $DATASTORE --collections PFS-F/raw/all

The result looks something like this::

    type      run                       id                  instrument arm dither pfs_design_id spectrograph detector exposure
    ---- ------------- ------------------------------------ ---------- --- ------ ------------- ------------ -------- --------
     raw PFS-F/raw/all 27217522-a357-5071-a32b-af97b5b8bee6      PFS-F   b    0.0             1            1        0        0
     raw PFS-F/raw/all 0ce0cbea-fe7c-589e-8259-30060bf20500      PFS-F   b    0.0             1            1        0        1
    [...]
     raw PFS-F/raw/all 570092eb-f571-5631-8d20-11acbeabc640      PFS-F   r    0.0             3            1        1       26
     raw PFS-F/raw/all f8e3ae71-2cdf-5e55-bc42-4a4fb913770c      PFS-F   r    0.0             4            1        1       27

Datasets can be accessed from python using the butler API,
which has some similarities to the Gen2 butler::

    from lsst.daf.butler import Butler
    butler = Butler("/path/to/datastore", collections="PFS-F/raw/all")
    raw = butler.get("raw", instrument="PFS-F", exposure=12, arm="r", spectrograph=1)
    rawImage = raw.getImage()

Notice that the ``raw`` data returned from the butler is now of type ``PfsRaw``,
which is a common interface for both the CCD and NIR detectors [#]_.
You can use ``butler.get("raw.exposure", ...)`` to get the exposure from the raw data directly.

.. [#] This will allow the up-the-ramp CR rejection to access the NIR reads.


Building calibs
^^^^^^^^^^^^^^^

Next we'll build the calibration products.
The first step is the bias frame::

    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/calib -o "$RERUN"/bias -p $DRP_STELLA_DIR/pipelines/bias.yaml -d "instrument='PFS-F' AND exposure.target_name = 'BIAS'" --fail-fast -c isr:doCrosstalk=False

The ``pipetask run`` command [#]_ is how we run a pipeline.
A task is an operation within the pipeline,
characterized by a set of dimensions that define the level at which it parallelizes,
and a set of inputs and outputs.
An instance of a task running on a single set of data at its parallelization level is called a "quantum".
A pipeline is built from the "quantum graph",
tracking the inputs and outputs between the various tasks.
When you run a pipeline with ``pipetask run``,
it first builds the pipeline and reports the number of quanta that will be run for each task::

    lsst.ctrl.mpexec.cmdLineFwk INFO: QuantumGraph contains 12 quanta for 2 tasks, graph ID: '1726845383.    6842682-77840'
    Quanta     Tasks    
    ------ -------------
        10           isr
         2 cpBiasCombine

The bias pipeline has only two tasks.
In this case, they are operating on 5 exposures, each with ``b`` and ``r`` arms,
so there are 10 ``isr`` quanta (instrument signature removal from each camera image)
and ``2`` ``cpBiasCombine`` quanta (combining the bias frames from each of the cameras).
The summary for a more complicated pipeline
(running the full science pipeline on 17 exposures)
is shown later.

.. [#] There are other ``pipetask`` commands that can be run,
       including ``build`` and ``qgraph`` which are used to
       create and visualize a pipeline,
       and ``cleanup`` and ``purge`` for deleting outputs.

The ``-j`` option specifies the number of cores to use in parallel,
and the ``-b`` option specifies the datastore to use.

The ``--instrument`` option specifies the instrument.
Here, we're specifying the simulated PFS instrument;
the proper PFS is ``lsst.obs.pfs.PrimeFocusSpectrograph`` [#]_.

.. [#] I've been told that it should be possible to replace
       these fully-qualified python names with shorter names
       (e.g., ``PFS-F`` and ``PFS``),
       but I've not had much success with that when I've tried it.
       Maybe that's fixed in the latest LSST version,
       or it requires some configuration.

The ``-i`` option specifies the input collections (comma-separated).
In this case, we are using the raw data and the calibration data (for the defects) [#]_.
Later we'll add other collections as we need them.

.. [#] We should be able to create a ``CHAINED`` collection that includes all of these.

The ``-o`` option specifies an output ``CHAINED`` collection.
The pipeline will write the output datasets to a ``RUN`` collection named after this,
with a timestamp appended (e.g., ``$RERUN/bias/20240918T181715Z``),
all chained together in the nominated output collection.

The ``-p`` option specifies the pipeline configuration file to use.
This is a YAML file in ``drp_stella/pipelines`` that describes the pipeline to run.
A pipeline is composed of multiple tasks,
each operating on a (potentially different) set of dimensions.
The pipeline configuration can also specify configuration overrides for each task,
including different dataset names to use as connections between the tasks
(useful for providing slightly different versions of the same dataset;
there'll be an example of this later).

The ``-d`` option specifies the data selection query.
The `query syntax`_ is similar to the ``WHERE`` clause in SQL, with some extensions.
In this case, we are selecting all the exposures that have a target name of ``BIAS``
and are from the ``PFS-F`` instrument.
Strings must be quoted with single quotes (``'``).
Ranges can be specified, like ``exposure IN (12..34:5)``,
which means all exposures from 12 to 34 (inclusive) in steps of 5.
The ``exposure`` dimension can be used directly to mean the exposure identifier,
but also has a variety of additional fields that can be used, including:

* ``exposure.exposure_time``: exposure time in seconds
* ``exposure.observation_type``: type of observation (e.g., ``BIAS``, ``DARK``, ``FLAT``, ``ARC``)
* ``exposure.target_name``: target name
* ``exposure.science_program``: science program name
* ``exposure.tracking_ra``, ``tracking_dec``: boresight position (ICRS)
* ``exposure.zenith_angle``: zenith angle in degrees
* ``exposure.lamps``: comma-separated list of lamps that were on

Other dimensions can also be used,
for example: ``exposure IN (12..34:5) AND arm = 'r' AND spectrograph = 3``.

.. _query syntax: https://pipelines.lsst.io/modules/lsst.daf.butler/queries.html#dimension-expressions

The ``-c`` option provides configuration overrides for the pipeline.
Note the difference in syntax from Gen2:
each configuration override requires a separate ``-c`` option,
and the overrides include a colon (``:``) between the task name and the configuration parameter name.
In this case, we are turning off the crosstalk correction
(since the simulated data does not have crosstalk).

You may see a ``--register-dataset-types`` option used with the ``pipetask run`` command.
This is used to register the dataset types from the pipeline in the butler registry.
It is only necessary to run this once for each pipeline,
and then it can be dropped for future runs of the same pipeline.

Some additional helpful options when debugging are:

* ``--skip-existing-in <COLLECTION>``:
  don't re-produce a dataset if it's present in the specified collection.
  This is helpful when you want to pick up from where a previous run stopped.
  Usually the ``<COLLECTION>`` specified here is the same as the output collection.
* ``--clobber-outputs``:
  clobber any existing datasets for a task
  (usually logging or metadata by-products of running the task).
* ``--pdb``:
  drop into the python debugger on an exception.
  This won't work with parallel processing, so check that you're not also using ``-j``.

The above three options (used together) are very useful when debugging a python exception in a pipeline run.

Once the pipeline has run and produced the bias frame,
we need to certify the calibration products::

    butler certify-calibrations $DATASTORE "$RERUN"/bias PFS-F/calib bias --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59

This command tells the butler to certify the ``bias`` datasets
in the ``$RERUN/bias`` collection as calibration products in the ``PFS-F/calib`` calib collection.
The ``--begin-date`` and ``--end-date`` options specify the validity range of the calibration products.

In order to manage the calibrations,
it may be necessary to be able to certify and decertify individual datasets.
This capability is not available with LSST's command-line tools,
but we have some scripts that can do this.
Here are some examples from working on real Subaru data [#]_::

    butlerDecertify.py /work/datastore PFS/calib dark --begin-date 2024-08-24T00:00:00 --id instrument=PFS arm=r spectrograph=2
    butlerDecertify.py /work/datastore PFS/calib dark --begin-date 2024-05-01T00:00:00 --end-date 2024-08-23T23:59:59 --id instrument=PFS arm=r spectrograph=2
    butlerCertify.py /work/datastore price/pipe2d-1036/dark/run16 PFS/calib dark --begin-date 2024-05-01T00:00:00 --id instrument=PFS arm=r spectrograph=2

.. [#] I discovered after certifying the darks that the run 18 r2 dark was bad
       (the intermitently misbehaving amplifier was bad),
       so I decertified it.
       Then I decertified the prior r2 dark so I could recertify it with different dates.

.. warning::
    Certifying a dataset as a calibration product
    ly tags it in the database as a calibration product
    and associates it with a validity timespan.
    It does not copy the dataset:
    the dataset is still a part of the ``$RERUN/bias/<timestamp>`` ``RUN`` collection,
    and removing that collection will remove the calibration dataset from the datastore.

However, that ``RUN`` collection also contains a bunch of intermediate datasets
which are unnecessarily consuming space,
in particular the ``biasProc`` datasets
(which are the outputs of running the ``isr`` task in the bias pipeline).
We can remove these with the following command::

    butlerCleanRun.py $DATASTORE $RERUN/bias/* biasProc

This will leave the ``$RERUN/bias/<timestamp>`` collection containing only the ``bias`` dataset
and some other small metadata datasets.
Note that our ``pipetask`` command specifies an output collection of ``$RERUN/bias``,
but we're specifying ``$RERUN/bias/*`` for the ``butlerCleanRun.py`` command,
which will delete all the timestamped ``RUN`` collections in the ``$RERUN/bias`` ``CHAINED`` collection.

You can also use the ``butler remove-runs`` command
to completely remove ``RUN`` collections
and ``butler remove-collections`` to remove ``CHAINED`` collections.

With the bias calibration product built and certified,
we can move on to the dark and flat, which follow the same pattern::

    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/calib -o "$RERUN"/dark -p '$DRP_STELLA_DIR/pipelines/dark.yaml' -d "instrument='PFS-F' AND exposure.target_name = 'DARK'" --fail-fast -c isr:doCrosstalk=False
    butler certify-calibrations $DATASTORE "$RERUN"/dark PFS-F/calib dark --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/dark/* darkProc
    
    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/calib -o "$RERUN"/flat -p '$DRP_STELLA_DIR/pipelines/flat.yaml' -d "instrument='PFS-F' AND exposure.target_name = 'FLAT'" --fail-fast -c isr:doCrosstalk=False
    butler certify-calibrations $DATASTORE "$RERUN"/flat PFS-F/calib fiberFlat --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/flat/* flatProc

The bias, dark and flat characterize the detector,
so now it's time to determine the detectorMap.
We first bootstrap a detectorMap from an arc and quartz::

    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/bootstrap -p '$DRP_STELLA_DIR/pipelines/bootstrap.yaml' -d "instrument='PFS-F' AND exposure IN (11, 22)" --fail-fast -c isr:doCrosstalk=False
    butler certify-calibrations $DATASTORE "$RERUN"/bootstrap PFS-F/bootstrap detectorMap_bootstrap --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/bootstrap/* postISRCCD

Here we've added the ``PFS-F/raw/pfsConfig`` collection to the input,
since we need the ``pfsConfig`` files to determine which fibers are illuminated.
Note that the arc and quartz are both specified as inputs in the same ``-d`` option.
The Gen3 middleware does not support multiple ``-d`` options to specify them independently,
but the task can determine which is which from the ``lamps`` field in the exposure.
The bootstrap pipeline writes a ``detectorMap_bootstrap`` dataset for each camera,
and we're certifying that in the ``PFS-F/bootstrap`` collection
(so it's independent of the best-quality detectorMaps we'll certify in ``PFS-F/calibs``).

When working with real data,
it will probably be necessary to run the bootstrap pipeline on each camera separately,
so that different ``-c bootstrap:spectralOffset=<WHATEVER>`` values can be used for each camera.

Now we have a rough detectorMap,
we can refine it and create the proper detectorMap::

    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/bootstrap,PFS-F/calib -o "$RERUN"/detectorMap -p '$DRP_STELLA_DIR/pipelines/detectorMap.yaml' -d "instrument='PFS-F' AND exposure.target_name = 'ARC'" -c isr:doCrosstalk=False -c measureCentroids:connections.calibDetectorMap=detectorMap_bootstrap -c fitDetectorMap:connections.slitOffsets=detectorMap_bootstrap.slitOffsets --fail-fast
    certifyDetectorMaps.py INTEGRATION $RERUN/detectorMap PFS-F/calib --instrument PFS-F --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/detectorMap/* postISRCCD

Here, we have modified two ``connections`` in the pipeline.
The ``measureCentroids`` task's ``calibDetectorMap`` input is a detectorMap
that provides the position at which to measure the centroids of the arc lines.
Usually this is set to the calibration detectorMap (``detectorMap_calib``),
but we don't have one of those yet.
Instead, we will configure this to use the bootstrap detectorMap (``detectorMap_bootstrap``) instead;
notice also that we're including the ``PFS-F/boostrap`` collection in the input.
Similarly, the ``fitDetectorMap`` task's ``slitOffsets`` input
is set to use the slit offsets from the bootstrap detectorMap [#]_.

.. [#] Some dataset types have components that can be accessed with a dot (``.``) operator.
       Other examples are ``raw.exposure`` to access an exposure from the raw data,
       ``postISRCCD.image`` or ``postISRCCD.mask`` to
       access the image and mask from an ISR-processed exposure.

The detectorMap pipeline writes a ``detectorMap_candidate`` dataset for each camera [#]_.
The ``certifyDetectorMaps.py`` script is used to certify the detectorMap datasets
instead of the usual ``butler certify-calibrations`` command.
This script copies the ``detectorMap_candidate`` as a ``detectorMap_calib``
and certifies it.

.. [#] We would like to write a ``detectorMap_calib`` dataset,
       but this is usually an input to the pipeline (for the ``measureCentroids`` task),
       so we need to use a different name for the output to avoid cycles.

Fiber profiles can be built in two different ways.
The ``fitFiberProfiles`` pipeline is equivalent to the Gen2 ``reduceProfiles`` script:
it fits a profile to multiple exposures simultaneously.
The ``measureFiberProfiles`` pipeline is equivalent to the Gen2 ``constructFiberProfiles`` script:
it measures the profile from a single exposure.
Here's how you run them::

    # fitFiberProfiles:
    defineFiberProfilesInputs.py $DATASTORE PFS-F integrationProfiles --bright 26 --bright 27
    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/fiberProfilesInputs,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/fitFiberProfiles -p '$DRP_STELLA_DIR/pipelines/fitFiberProfiles.yaml' -d "profiles_run = 'integrationProfiles'" -c fitProfiles:profiles.profileSwath=2000 -c fitProfiles:profiles.profileOversample=3 --fail-fast
    
    # measureFiberProfiles:
    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/measureFiberProfiles -p '$DRP_STELLA_DIR/pipelines/measureFiberProfiles.yaml' -d "instrument='PFS-F' AND exposure.target_name IN ('FLAT_ODD', 'FLAT_EVEN')" -c isr:doCrosstalk=False --fail-fast
    
    butler certify-calibrations $DATASTORE "$RERUN"/fitFiberProfiles PFS-F/calib fiberProfiles --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/fitFiberProfiles/* postISRCCD

Because it involves multiple groups of exposures,
the ``fitFiberProfiles`` pipeline is a bit more complicated
and requires defining the inputs to the pipeline ahead of time.
The ``defineFiberProfilesInputs.py`` script is used to define the inputs
for the different groups of exposures.
When working on real data, we typically have four groups of several exposures each,
and each group contains "bright" (select fibers deliberately exposed)
and "dark" (all fibers hidden) exposures.
In the integration test, we only have two groups with a single bright exposure each, and no dark exposures.
For real data, the command might look like::

    defineFiberProfilesInputs.py $DATASTORE PFS run18_brn --bright 113855..113863 --dark 113845..113853 --bright 113903..113911 --dark 113893..113901 --bright 114190..114198 --dark 114180..114188 --bright 114238..114246 --dark 114228..114236

This creates a ``profiles_run`` dimension value and associates those exposures with it.
A file describing the roles of the exposures
is written in the ``<instrument>/fiberProfilesInputs`` collection,
so this must be included in the inputs for the ``fitFiberProfiles`` pipeline.
We can use the ``profiles_run`` value in the data selection query,
as that is linked to all the required exposures.

Note that in the Gen3 pipeline, the fiberProfiles do not include the quartz spectrum normalization.
The quartz spectrum used for normalization is supplied by the ``fiberNorms`` [#]_::

    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/fiberNorms -p '$DRP_STELLA_DIR/pipelines/fiberNorms.yaml' -d "instrument='PFS-F' AND exposure.target_name = 'FLAT' AND dither = 0.0" -c isr:doCrosstalk=False -c reduceExposure:doApplyScreenResponse=False -c reduceExposure:doBlackSpotCorrection=False --fail-fast
    butler certify-calibrations $DATASTORE "$RERUN"/fiberNorms PFS-F/calib fiberNorms_calib --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
    butlerCleanRun.py $DATASTORE $RERUN/fiberNorms/* postISRCCD

The ``fiberNorms`` pipeline combines the extracted spectra from multiple quartz exposures,
and writes the output as ``fiberNorms_calib``.

.. [#] I.e., the ``fiberNorms_calib`` is no longer a ratio of quartz spectra,
       but the extracted quartz spectra themselves.
       This is due to convenience
       (since including the quartz spectrum in the fiberProfiles
       would require an extra step in their construction),
       but it's also a change that had been suggested for the Gen2 pipeline,
       as it greatly simplifies the flux calibration process.


Processing science data
^^^^^^^^^^^^^^^^^^^^^^^

Now that we have the calibration products built,
we can process the science data.
There are a few pipelines available:

* ``reduceExposure``: process an exposure through merging arms,
  producing ``postISRCCD``, ``pfsArm``, ``lines``, ``detectorMap``,
  ``pfsMerged``, ``sky1d`` and ``fiberNorms``.
  This can be used to process quartz exposures
  (or sky exposures when flux calibration is not wanted).
  The ``calexp`` data product, familiar from the Gen2 pipeline,
  is not produced by the Gen3 pipeline;
  instead, use the ``postISRCCD`` data product for the processed image.
  The ``fiberNorms`` dataset is only produced for quartz exposures;
  contrary to the ``fiberNorms_calib`` product, this is a *residual* normalization
  equal to the ratio of the observed quartz spectrum to the ``fiberNorms_calib`` spectrum
  (after applying screen responses and the like).
* ``calibrateExposure``: adds the flux calibration to ``reduceExposure``,
  producing ``pfsFluxReference``, ``fluxCal`` and ``pfsCalibrated``.
  This can be used to process single sky exposures.
  This is not demonstrated below,
  but its use is similar to that for ``reduceExposure``.
* ``science``: adds the spectral coaddition,
  producing ``pfsCoadd``.
  This can be used to process multiple sky exposures together.

Because we need to be able to distinguish coadds formed from different combinations of exposures [#]_,
it's necessary to define the inputs to the coaddition before running the ``science`` pipeline.
This is not required for the ``reduceExposure`` or ``calibrateExposure`` pipelines,
but it doesn't hurt to define the inputs for them as well if you want a simple way to refer to them.
The integration test defines two combinations::

    defineCombination.py $DATASTORE PFS-F object --where "exposure.target_name = 'OBJECT'"
    defineCombination.py $DATASTORE PFS-F quartz --where "exposure.target_name = 'FLAT' AND dither = 0.0"

.. [#] For example, one could imagine coadding all available exposures,
       or only even-numbered exposures,
       or only exposures with an long exposure time.

A combination can be defined with a ``--where`` option,
which takes a query string like for the ``-d`` option of ``pipetask run``.
Alternatively, a combination can be defined by simply listing the exposure identifiers::

    defineCombination.py $DATASTORE PFS-F someExposures 123 124 125

Now we can run the pipeline::

    # Single exposure pipeline
    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/reduceExposure -p '$DRP_STELLA_DIR/pipelines/reduceExposure.yaml' -d "combination IN ('object', 'quartz')" --fail-fast -c isr:doCrosstalk=False -c reduceExposure:doApplyScreenResponse=False -c reduceExposure:doBlackSpotCorrection=False -c 'reduceExposure:targetType=[SCIENCE, SKY, FLUXSTD]'

    # Science pipeline
    pipetask run --register-dataset-types -j $CORES -b $DATASTORE --instrument lsst.obs.pfs.PfsSimulator -i PFS-F/raw/all,PFS-F/raw/pfsConfig,PFS-F/calib -o "$RERUN"/science -p '$DRP_STELLA_DIR/pipelines/science.yaml' -d "combination = 'object'" --fail-fast -c isr:doCrosstalk=False -c fitFluxCal:fitFocalPlane.polyOrder=0 -c reduceExposure:doApplyScreenResponse=False -c reduceExposure:doBlackSpotCorrection=False -c 'reduceExposure:targetType=[SCIENCE, SKY, FLUXSTD]'

Notice that in the first case we're running the ``reduceExposure`` pipeline,
selecting the ``object`` and ``quartz`` combinations that we defined earlier.
We've turned off the screen response and black spot correction
(which are not appropriate for the simulated data),
and we've set the ``targetType`` configuration parameter
to disable extracting spectra for the (many) unilluminated fibers
(we don't have good fiber profiles for them anyway).

The ``science`` pipeline is similar,
with the only important change that we're setting the flux calibration fitting order to zero
(because there aren't enough fibers to fit a higher-order polynomial).
Note that we do not have to run the ``reduceExposure`` pipeline before we run the ``science`` pipeline
(a single command is sufficient to run the entire pipeline):
the ``science`` pipeline knows how to produce all the necessary intermediate datasets itself,
and the above two commands are completely independent: they do not share any intermediate datasets.
However, we could have first run the ``reduceExposure`` pipeline
and then fed the outputs from that pipeline into the the ``science`` pipeline
by including ``$RERUN/reduceExposure`` in the list of input collections for the ``science`` pipeline.

There are some important differences in the data products
produced by the Gen3 pipeline compared to the Gen2 pipeline.
For the sake of efficiency
(both in terms of processing time and reduced file numbers),
the single-spectrum Gen2 products (``pfsSingle`` and ``pfsObject``)
are written as multiple-spectrum Gen3 products per ``cat_id`` [#]_
(``pfsCalibrated`` and ``pfsCoadd``).
The equivalent of a ``pfsObject`` can be retrieved directly from the ``pfsCoadd`` dataset [#]_::

    from lsst.daf.butler import Butler
    butler = Butler("INTEGRATION", collections="integration/science")
    pfsObject = butler.get("pfsCoadd.single", cat_id=1, combination="object", parameters=dict(objId=55))

.. [#] Depending on how ``catId`` is used in the pfsConfigs for science observing,
        we might change this later to include ``skymap, tract, patch``
        or some other spatial index.

.. [#] This is inefficient, because the code reads the entire ``pfsCoadd`` dataset
        before providing the single matching spectrum.
        However, it may be a useful convenience in some circumstances.

Note that the ``objId`` needs to be specified in the ``parameters`` dictionary,
rather than as a separate argument to the ``get`` method
because it's a parameter for the formatter that reads the dataset
and not a dimension of the dataset itself.

Another important difference is that the Gen3 butler names files itself,
rather than following the PFS datamodel.
In order to deliver products according to the PFS datamodel,
we need to export the products from the butler::

    exportPfsProducts.py -b $DATASTORE -i PFS-F/raw/pfsConfig,"$RERUN"/science -o export

This creates a directory tree within the ``export`` directory
with links to the files in the butler datastore,
and individual spectrum files for the ``pfsSingle`` and ``pfsObject`` datasets.
You can then deliver the ``export`` directory to the consumer.

Running the entire integration test with 20 cores at Hilo takes about 18 minutes of runtime.
