.. subtractSky2d:

Two-dimensional Sky Subtraction
===============================

Two-dimensional sky subtraction is part of ``reduceExposure``.
Because fibers can be separated by as few as 5 pixels,
the flux in the wings of the PSF from bright sky lines in one fiber can leak into neighbouring fibers,
contaminating the extracted spectra.
The goal of this module is to model and subtract the bright sky lines from the image
before extraction of the spectra.

This module will be provided multiple images,
comprising all arms of the same kind within an exposure
(e.g., the red arms from each of the spectrographs);
this allows modelling of the spectrum over the entire focal plane.
This module will be provided a 2D PSF model [#]_ for each exposure,
although the class representing this is yet to be defined;
it will likely look like the |LSST Psf class|_.
It will also be provided a ``FiberTraceSet`` and ``DetectorMap`` for each exposure
so that it knows the location of sky lines.
Finally, a ``PfsConfig`` allows identification of the different targets,
including sky fibers and blocked or broken fibers.
The module should subtract the sky from the input exposures,
and return a persistable object that represents the sky that has been subtracted.

.. [#] Neven Caplar is working on measuring the 2D PSF using out-of-focus images,
       but we could imagine an alternative implementation using a classic image PSF code,
       such as `PSFEx`_ or `PIFF`.

.. _PSFEx: https://www.astromatic.net/software/psfex
.. _PIFF: https://github.com/rmjarvis/Piff
.. |LSST Psf class| replace:: LSST ``Psf`` class
.. _LSST Psf class: https://github.com/lsst/afw/blob/master/include/lsst/afw/detection/Psf.h

Here is an example definition::

    class SubtractSky2DTask(lsst.pipe.base.Task):
        def run(self, exposureList, pfsConfig, psfList, fiberTraceList, detectorMapList):
            """Measure and subtract sky from 2D spectra image

            Parameters
            ----------
            exposureList : iterable of `lsst.afw.image.Exposure`
                Images from which to subtract sky.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Top-end configuration, for identifying sky fibers.
            psfList : iterable of PSFs (type TBD)
                Point-spread functions.
            fiberTraceList : iterable of `pfs.drp.stella.FiberTraceSet`
                Fiber traces.
            detectorMapList : iterable of `pfs.drp.stella.DetectorMap`
                Mapping of fiber,wavelength to x,y.

            Returns
            -------
            sky2d : `SomePersistable`
                2D sky subtraction solution.
            """
            sky2d = self.measureSky(...)
            self.subtractSky(...)
            return sky2d
