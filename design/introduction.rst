Introduction
------------

The `Prime Focus Spectrograph`_ consists of approximately 2400 science fibers,
distributed over a 1.3 deg\ :sup:`2` field,
feeding four spectrographs, each comprised of blue, red and infrared arms
which together cover wavelengths of 0.38 - 1.26 microns.
It is the responsibility of the 2D Data Reduction Pipeline (DRP) to process the raw data
to produce wavelength-calibrated, flux-calibrated coadded spectra suitable for science investigations.
This document outlines a design for the 2D DRP, including
the data flow,
the support classes,
the functional modules,
and the datasets that will be produced.

.. _Prime Focus Spectrograph: https://pfs.ipmu.jp


The 2D DRP will be built following the same philosophy as the `LSST stack`_ and the `Hyper Suprime-Cam pipeline`_.
The pipeline will be written in `Python`_, for ease of development, maintenance and reading,
while classes and functions requiring the performance of a compiled language will be implemented in `C++`_
and wrapped using `pybind11`_.
As far as is practical given the smaller size of our development team,
we will follow the coding styles and policies in the `LSST Developer Guide`_.

.. _LSST stack: https://pipelines.lsst.io
.. _Hyper Suprime-Cam pipeline: http://adsabs.harvard.edu/cgi-bin/nph-data_query?bibcode=2018PASJ...70S...5B&db_key=AST&link_type=ABSTRACT
.. _Python: https://www.python.org
.. _C++: https://en.wikipedia.org/wiki/C%2B%2B
.. _pybind11: https://github.com/pybind/pybind11
.. _LSST Developer Guide: https://developer.lsst.io

