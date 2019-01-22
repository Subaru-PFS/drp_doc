.. _introduction:

Introduction
============

The `Prime Focus Spectrograph`_ consists of approximately 2400 science fibers,
distributed over a 1.3 deg\ :sup:`2` field,
feeding four spectrographs, each comprised of blue, red and infrared arms
which together cover wavelengths of 0.38 - 1.26 microns.
It is the responsibility of the 2D Data Reduction Pipeline (DRP) to process the raw data
to produce wavelength-calibrated, flux-calibrated coadded spectra suitable for science investigations.

.. _Prime Focus Spectrograph: https://pfs.ipmu.jp

This document describes how to use the pipeline software to deliver science spectra.
First we outline how to `install the software`_
and how to use our package management software (`EUPS`_).
Next we outline how to `ingest raw data`_ into a data repository,
and give an overview of `common command-line arguments`_ for the pipeline scripts.
Then we describe how to use the two main components to the DRP to process that data:
the `calib construction pipeline`_ and the `science pipeline`_.
Next, we give a survey of some of the `building blocks`_ for the pipeline.
Finally, we give suggestions on where you can `get help`_.

.. _install the software: :ref:`installation`
.. _EUPS: :ref:`eups`
.. _ingest raw data: :ref:`ingest`
.. _common command-line arguments: :ref:`commonArguments`
.. _calib construction pipeline: :ref:`calibs`
.. _science pipeline: :ref:`pipeline`
.. _building blocks: :ref:`buildingBlocks`
.. _get help: :ref:`help`
