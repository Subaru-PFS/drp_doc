###########
2D DRP Plan
###########

Doc Code: PFS-DRP-PRU030002-01

Introduction
============

Aim
---

This document describes the current working plan for DRP development, 
covering the period from October 2018 until the end of operations.


Data flow
---------

.. figure:: DRP-flow.png
  :width: 80%

The data flow for 2D DRP processing is depicted in the figure above. Blue boxes indicate main processing units, and white boxes key input data types.
The instrument and its corresponding simulator are shown in central green boxes. The outputs of the simulator and instrument are in general the same (as expected if the simulator simulates the instrument correctly), with the exception that the instrument will provide bias, darks and flats that can be later used by the simulator.


Notes
-----

Each 2D-DRP release is named according to an incremental version number of the form ``<major>.<minor>`` . 
For historical reasons, the initial version described in this plan is 4.0 .



2DDRP-4.0 (Sep 2018)
====================

This is the initial release of the pipeline. Used for SM1 r-channel testing at LAM.

- Basic functionality
- Low-level test harness

2DDRP-5.0 (Dec 2018)
====================

This is an intermediate release for NAOJ to test their software for the HSC collaboration prior to the HSC PDR2 release.

- Packaged SIM2D
- Packaged 2D DRP
- Bug fixes
- data model for 2D (and 1D) consistent
- agreed file formats and directory locations (or through DB)

2DDRP-6.0 (Apr 2019)
====================

Initial end-to-end demonstration of pipeline. Integration test incorporates the 2D simulator,
that provides test quartz, arcs and science data. Quick processing of exposures within 15 minutes is required. If this is not possible using the full DRP pipeline, a configuration of that pipeline which makes use of more approximate models (eg a more approximate PSF model) will be introduced to achieve this goal.  

- all 3 arms (R, B, N and M) processed 
- 3 arms merged
- initial flat-fielding in accordance to new framework
- detector map generated
- initial flux calibration (TBC)
- more complete test harness
- Initial 2D PSF model with color dependence
- initial 'Quick' DRP available and demonstratable

2DDRP-7.0 (July 2019)
====================

Version for early PSF commissioning. Sky data from LAM used for PSF model color dependence. 'Quick' DRP as well as the 'full' DRP should be available. Quick DRP should function at LAM as well as at the summit, in coordination with the ICS. 2D sky subtraction using arcs (TBC). Robust and simple 1D sky subtraction.

- Initial telluric absorption
- Initial 2D sky subtraction (to 2% [TBC] of the faint sky continuum between the lines)
- Initial 1D sky subtraction
- Quick DRP available 

2DDRP-8.0 (Mar 2020)
====================

Updated version for commissioning. Raster scan observations will take place at this time to refine the accuracy of fiber positioning. For this, Quick DRP will output numeric data of wavelength-calibrated, flux-calibrated one-dimensionalized spectra. with improvements based on acquired data during the early commissioning phase. Updates to the pipeline will be made based on acquired data (bright stars), from SM1 and SM2 modules initially.

- Updated 2D PSF model
- Improved telluric absorption
- Updated 2D sky subtraction (to 1% of the faint sky continuum between the lines [TBC])
- Performance (speed) improved 
- Updated Quick DRP for wavelength-calibrated spectra

2DDRP-9.0 (Sep 2020)
====================

Intermediate release with functional updates. Updates to the pipeline will be made based on acquired data (faint as well as bright stars) from SM3, as well as the SM1 and SM2 modules.


2DDRP-10.0 (Jan 2021)
====================

Further improvements. Pipeline incorporates acquired data from all 4 SM modules.

- Bug fixes
- Missing functions
- Refactoring
- Performance (speed) improvements
- sky subtraction to 0.5% of the faint sky continuum between the lines




