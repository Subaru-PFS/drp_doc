.. measurePsf:

PSF Measurement
===============

PSF measurement is part of ``reduceExposure``.
The goal of this module is to construct a PSF model for each of the arms in an exposure,
which will be used for the `subtractSky2d` module.

The module will operate on all arms of the same kind within an exposure
(e.g., the red arms from each of the spectrographs);
this allows modelling of quantities over the entire focal plane.
It will be provided a list of butler data references
(allowing it to load any persisted parameters used in the PSF fitting)
and a list of images for the exposure.
It should return a PSF for each of the exposures.

Here is an example definition::

    class MeasurePsfTask(lsst.pipe.base.Task):
        def run(self, sensorRefList, exposureList):
            """Measure the PSF for an exposure over the entire spectrograph

            We operate on the entire spectrograph in case there are parameters
            that are shared between spectrographs.

            Parameters
            ----------
            sensorRefList : iterable of `lsst.daf.persistence.ButlerDataRef`
                List of data references for each sensor in an exposure.
            exposureList : iterable of `lsst.afw.image.Exposure`
                List of images of each sensor in an exposure.

            Returns
            -------
            psfList : `list` of PSFs (type TBD)
                List of point-spread functions.
            """
            ...
            return pfsList
