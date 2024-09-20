Use of the Gen3 Pipeline
------------------------

Use at Hilo
^^^^^^^^^^^

I have set up a Gen3 instance for the Subaru data at Hilo.
The datastore is ``/work/datastore`` [#]_,
and the registry is a PostgreSQL database hosted on ``pfsa-db``.
I have ingested all raw files from run 11 (2023 April) through run 18 (2024 September).

.. [#] This is a symlink to the actual datastore (``/work/datastore-20240913``)
       so we can do versioning if that proves necessary.
       The datastore should be relocatable.

Users need to create a file ``~/.lsst/db-auth.yaml``
and set it to user-only read/write (``chmod 600 ~/.lsst/db-auth.yaml``).
The file should contain::

    - url: postgresql://pfsa-db:5435/drp
      username: pfs
      password: PASSWORD

(Replace ``PASSWORD`` with the actual database password; ask if you don't know it.)

.. note:: Please check that you have ``umask 002`` in your shell startup files
    so that others can read the files you create.

I have created calibs for run 18 (2024 August),
and certified them in the collection ``PFS/calib``.
Keep in mind that there is a single ``fiberNorms`` for the entire run:
I have not paid any attention to customizing ``fiberNorms`` for particular exposures.
Nevertheless, you should be able to run the pipeline on data from run 18.

The raw data are in collection ``PFS/raw/all``.
The pfsConfigs are in collection ``PFS/pfsConfig``.
The calibs are in collection ``PFS/calib``.
I have created a ``CHAINED`` collection containing the above three collections,
called ``PFS/default``; you can use this collection instead of specifying the three collections separately.

You shouldn't need to include ``--register-dataset-types`` in your ``pipetask run`` command,
as the dataset types should already be registered.

Here's how I tested that it works::

    defineCombination.py /work/datastore PFS price/pipe2d-1036/ge-faint 110995 110996 111169 111170 111172 111172 111321 111322 111347 111348 111486 111488 111489 111490 111493 111628 111629 111630 111631 111803 111804 111805
    pipetask run -b /work/datastore --instrument lsst.obs.pfs.PrimeFocusSpectrograph -i PFS/default -o price/pipe2d-1036/ge-faint -p '$DRP_STELLA_DIR/pipelines/science.yaml' -d "combination = 'price/pipe2d-1036/ge-faint'" --fail-fast -j 60

    Quanta        Tasks       
    ------ -------------------
       210                 isr
       210      reduceExposure
        21           mergeArms
        63          fiberNorms
        21 fitPfsFluxReference
        21          fitFluxCal
         5        coaddSpectra

Perhaps you'd like to create a combination for a different data set and run the pipeline on it?

.. note::
    Because the Gen3 transition addresses the middleware,
    rather than the algorithms that process the data,
    the science performance of the pipeline should not suffer from this transition.
    However, it is possible that the transition has introduced new bugs,
    or a feature has accidentally slipped out.
    If you notice any issues with the pipeline,
    or have any questions or concerns,
    please report them on the PFS Slack in the ``#drp-2d`` channel.
    This is a new way of working for us,
    so I will be monitoring the channel closely to help with any issues that arise.


Policies
^^^^^^^^

There are a number of shared namespaces in the registry,
for collections, fiberProfiles inputs, and combinations.
I propose the following policies for these namespaces to minimize conflicts and confusion.

Collections should generally be named with the username of the creator as the initial component.
After that, the creator is free to name the collection as they see fit,
but it is recommended that the name be descriptive
and contain information to identify the purpose of the collection
(e.g., so that obsolete collections can be removed in the event of a space crunch).
One example would be to use Jira ticket names, e.g., ``price/pipe2d-1036/bias``.
Another might be to use the date, linking back to my own personal notes, e.g., ``price/20240913``.
An exception to naming collections after the creator
is when the collection is a long-lived shared resource,
such as calibs (e.g., ``calib/detectorMap/2025sep/brn``)
or science production run (e.g., ``dr1.2``).
Although it's possible to include multiple instruments in a Gen3 registry,
I can't see us doing that in practice,
and so I don't think it's necessary to include the instrument name in the collection name
except as a way to distinguish official collections (e.g., ``PFS/calib``).

FiberProfiles inputs names (set by ``defineFiberProfilesInputs.py``)
should be named after the observing run and spectroscopic mode.
For example, ``run18_brn`` or ``2026may_m``.
There is no need to prefix the username to these names,
as these will be relatively rare,
and we will all share the same sets of inputs.
If there is a need to subset these for development purposes,
then the name should by prefixed with the developer's username.

I expect combination names to have a use pattern closer to that of the collections,
but it's not yet clear to me exactly how we will use them.
In general these will be a shared resource,
and so they shouldn't need a username prefix unless for development purposes.
I expect we will want to create combinations for
observations (principally) devoted to a single science project,
with a variety of timescales (night, run, multiple runs).
For these, I suggest naming patterns something like:

* Single night: ``<scienceProject>/<date>``, e.g., ``ssp-ge/20240920``
* Single run: ``<scienceProject>/<run>``, e.g., ``ssp-ga/2026may``
* Multiple runs: ``scienceProject>/<startRun>-<endRun>``, e.g., ``ssp-c/2025may-2026sep``

For service observations with fibers devoted to a mix of science projects,
it may be sufficient to only have a single combination per run,
e.g., ``shared/2025aug``.
