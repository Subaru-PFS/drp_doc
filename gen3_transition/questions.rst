Questions answered
------------------

Here are some questions that have been answered in the course of the transition.

Reading raws
~~~~~~~~~~~~

Reading the ``raw`` datasetType is a bit tricky::

   >>> butler = Butler("/work/datastore", collections="PFS/raw/all")
   >>> butler.get("raw", exposure=115191, arm="r", spectrograph=2, instrument="PFS")

results in a ``KeyError``
because the LSST system wants ``raw`` datasets to be associated with a ``detector`` dimension,
and we typically don't provide that directly with PFS
(we use ``arm`` and ``spectrograph``).

Here's how you can get the raw data::

    >>> refList = list(butler.registry.queryDatasets("raw", exposure=115191, arm="r", spectrograph=2, instrument="PFS"))
    >>> print([ref.dataId.full for ref in refList])
    [{instrument: 'PFS', arm: 'r', dither: -0.00071, pfs_design_id: 2035511409815847451, spectrograph: 2, detector: 4, exposure: 115191}]
    >>> raw = butler.get(refList[0])
    >>> print(raw)
    <lsst.obs.pfs.raw.PfsRaw object at 0x7f5857d935d0>

``butler.registry.queryDatasets`` does a query to figure out the ``detector`` behind the scenes,
and provides an iterator to "dataset references"
that can be used with ``butler.get()`` to retrieve all the datasets that satisfy the query
(in this case, we've specified ``instrument``, ``exposure``, ``arm``, and ``spectrograph``,
so there is only one dataset that satisfies the query).

Note that the ``raw`` datasetType now provides a ``PfsRaw`` object,
not an ``Exposure`` or ``Image`` [#]_.
You can do ``butler.registry.queryDatasets("raw.exposure", ...)`` to get the ``Exposure``,
or specify ``"raw.image"`` to get the ``Image``,
or you can call ``getImage()`` on the ``PfsRaw`` object to get the ``Image`` [#]_.

.. [#] This was done in order to provide a common interface to CCD and NIR data.
.. [#] For NIR, this would provide the "CDS image".

We have tried to make it so that other dataset types besides ``raw``
(e.g., ``postISRCCD``, ``pfsArm``, etc.)
do not suffer from this problem,
but ``raw`` is defined by LSST and it's scary to contemplate changing it.


Deleting collections
~~~~~~~~~~~~~~~~~~~~

``butler remove-collections`` will remove non-``RUN`` collections.
This is generally used to un-chain your output collection
from the timestamped ``RUN`` collections contained within.
``butler remove-runs`` will remove ``RUN`` collections and the data they contain.
``butlerCleanRun.py`` allows you to remove particular dataset types from ``RUN`` collections.
Use these commands with the ``-h`` flag to get more information.

To completely remove an output collection, you probably want to do something like::

    butler remove-collections $DATASTORE price/pipe2d-12345
    butler remove-runs $DATASTORE price/pipe2d-12345/*

Notice that the first command removes the chain, and the second removes the runs (and the data).
The order in which these commands are run shouldn't matter.

.. warning:: Never use ``rm`` in the datastore unless it's just to remove (verified) empty directories.

