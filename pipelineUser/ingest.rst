.. _ingest:

Ingestion of raw data
=====================

All data, both raw and the pipeline products,
live in a "data repository".
Ideally, from the point of view of the user,
this "data repository" is a black box that contains the data:
the user should never assume a particular implementation for the data repository
(including directory structure, filenames and file formats),
but instead access it through the :ref:`butler`.

.. note:: The butler that we currently use is based on the second generation ("Gen2") LSST middleware,
          and all PFS 2D DRP operations are hard-wired to expect that.
          LSST has been developing a new generation of middleware ("Gen3")
          which we will adopt at a suitable time.
          These two middleware generations have different designs,
          and the data repositories they employ are not directly interchangeable,
          but we expect that there will be a facility available to convert Gen2 data repositories to Gen3.

Here, we create a data repository and stuff raw data into it,
for use by the pipeline.

Creating the data repository
----------------------------

Create the data repository by making an empty directory,
and inserting a ``_mapper`` file with the correct contents::

    mkdir -p /path/to/dataRepo
    echo lsst.obs.pfs.PfsMapper > /path/to/dataRepo/_mapper


Ingesting the data
------------------

Use ``ingestPfsImages.py`` to ingest data into the data repository::

    ingestPfsImages.py /path/to/dataRepo /path/to/rawData/PFFA*.fits

.. note:: The ``ingestPfsImages.py`` script assumes that
          the ``pfsConfig`` files are in the same location as the raw images.
          The ``pfsConfig`` files are required in order to reduce the data,
          and will be ingested along with the raw images.

The default behaviour of ``ingestPfsImages.py`` is to link the files into the data repository.
This behaviour can be changed with the ``--mode`` command-line argument
(e.g. ``--mode move`` or ``--mode copy``).

Run ``ingestPfsImages.py`` with the ``--help`` command-line argument
for an extensive list of command-line arguments that are supported.

.. note:: ``ingestPfsImages.py`` will not work well with the ``-j`` argument (multiple processes)
          as it is designed to run with a single process.


.. _butler:

Data Butler
-----------

Once data have been ingested into the data repository,
you can access it through the data butler.
The data butler finds data of the requested dataset type
on the basis of keyword-value pairs that identify the data,
e.g., in python::

    >>> from lsst.daf.persistence import Butler
    >>> butler = Butler("/path/to/dataRepo")
    >>> image = butler.get("raw", visit=12, spectrograph=1, arm="r")
    >>> image
    <lsst.afw.image.exposure.exposure.ExposureU object at 0x7ff0b4cff490>

The keywords ``visit``, ``spectrograph`` and ``arm`` are sufficient to identify a single image,
but they are not all that is available.
You can search the repository for keyword values using ``Butler.queryMetadata``::

    >>> keywords = ["visit", "spectrograph", "arm"]
    >>> for values in butler.queryMetadata("raw", keywords, field="OBJECT"):
    ...     dataId = dict(zip(keywords, values))
    ...     print(dataId, butler.get("raw", dataId))
    ... 
    {'visit': 32, 'spectrograph': 1, 'arm': 'r'} <lsst.afw.image.exposure.exposure.ExposureU object at 0x7f1fd22e4880>
    {'visit': 33, 'spectrograph': 1, 'arm': 'r'} <lsst.afw.image.exposure.exposure.ExposureU object at 0x7f1fd22e4dc0>
