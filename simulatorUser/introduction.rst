.. _introduction:

Introduction
============

The `Prime Focus Spectrograph`_ consists of approximately 2400 science fibers,
distributed over a 1.3 deg\ :sup:`2` field,
feeding four spectrographs, each comprised of blue, red and infrared arms
which together cover wavelengths of 0.38 - 1.26 microns.
The 2D Data Reduction Pipeline (DRP) Simulator is a software facility
for producing images simulating the images that PFS will produce.
This allows software and science development and integration tests to be performed
long before the existence of real images from PFS.

.. _Prime Focus Spectrograph: https://pfs.ipmu.jp

This document is a guide to the user of the Simulator software.
We will first give instructions on `installing the Simulator software`_.
Then, we will outline the `features of the Simulator`_
and give advice on `how to use the Simulator`_.

.. _installing the Simulator software: :ref:`installation`
.. _features of the Simulator: :ref:`features`
.. _how to use the Simulator: :ref:`use`

Throughout, the user should be aware that the simulator is **not yet ready for open use**,
but we are making the current version available in the hope that it will be useful.
Users are welcome to contact the development team with questions,
requests for help,
or suggestions for prioritising future development,
either through the ``#drp-2d`` channel on `Slack`_,
or by e-mail to ``pfs_software@astro.princeton.edu``.

.. _Slack: http://sumire-pfs.slack.com
