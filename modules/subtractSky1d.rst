.. subtractSky1d:

One-dimensional Sky Subtraction
===============================

One-dimensional sky subtraction is part of ``mergeArms``.
The goal of this module is to model and subtract the sky from the spectra.
We will use it either to clean up correlated spectral residuals left by the two-dimensional sky subtraction
or to perform sky subtraction entirely in the spectral domain
(e.g., if the two-dimensional sky subtraction is too CPU-intensive to use for quick-look reductions).

This module will be provided the spectra from all arms of all spectrographs for the exposure;
this allows modelling of the spectrum over the entire focal plane.
This module will also be provided a line-spread function (LSF) model for each exposure,
although the class representing this is yet to be defined;
it will likely look like a one-dimensional version of the |LSST Psf class|_.
Finally, a ``PfsConfig`` allows identification of the different targets,
including sky fibers and blocked or broken fibers.
The module should subtract the sky from the input spectra,
and return a persistable object that represents the sky that has been subtracted.

.. |LSST Psf class| replace:: LSST ``Psf`` class
.. _LSST Psf class: https://github.com/lsst/afw/blob/master/include/lsst/afw/detection/Psf.h

Here is an example definition::

    class SubtractSky1DTask(lsst.pipe.base.Task):
        def run(self, spectraList, pfsConfig, lsfList):
            """Measure and subtract the sky from the 1D spectra

            Parameters
            ----------
            spectraList : iterable of `pfs.datamodel.PfsSpectra`
                List of spectra from which to subtract the sky.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Configuration of the top-end, for identifying sky fibers.
            lsfList : iterable of LSF (type TBD)
                List of line-spread functions.

            Returns
            -------
            sky1d : `SomePersistable`
                1D sky model.
            """
            sky1d = self.measureSky(...)
            self.subtractSky(...)
            return sky1d
