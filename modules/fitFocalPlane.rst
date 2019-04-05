.. fitFocalPlane:

Focal Plane Function Fitting
============================

Fitting a vector function over the focal plane is a common operation,
which can be used in the two-dimensional and one-dimensional sky subtractions,
PSF measurement, and flux calibration modules.

The goal of this module is to fit a vector function over the focal plane.
This vector function might be the strength of sky lines,
the response of the instrument,
or some other measurements made from the spectrum for a subset of fibers.

This module will be provided with ``M`` vectors of length ``N``,
along with corresponding errors and boolean masks,
and a list of identifiers for the appropriate fibers.
A ``PfsConfig`` will also be provided,
from which can be obtained the position of the target on the sky or on the focal plane,
and the intended position on the focal plane [#]_.
The module should return a persistable object that represents the fit.

.. [#] Early versions of this module might simply fit
       the vectors as a function of focal plane position,
       but one can imagine more sophisticated versions that might
       use the distance between the actual and intended fiber position
       to weight the fit, or even as a variable in the fit.

In addition to the usual ``run`` method,
the module's ``Task`` should also implement an ``apply`` method
that takes the result from the ``run`` method and applies it to a list of fibers.
Like the ``run`` method, this also requires a ``PfsConfig``
to get the required information on fiber positions.

Here is an example definition::

    class FitFocalPlaneTask(lsst.pipe.base.Task):
        def run(self, vectors, errors, masks, fiberIdList, pfsConfig):
            """Fit a vector function over the focal plane

            Parameters
            ----------
            vectors : `numpy.ndarray` of shape ``(M, N)``
                Measured vectors of length ``N`` for ``M`` positions.
            errors : `numpy.ndarray` of shape ``(M, N)``
                Errors in the measured vectors.
            masks : `numpy.ndarray` of shape ``(M, N)``
                Non-zero entries should be masked in the fit. If a boolean array,
                we'll mask entries where this is ``True``.
            fiberIdList : iterable of `int` of length ``M``
                Fibers being fit.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Top-end configuration, for getting the fiber centers.

            Returns
            -------
            fit : `SomePersistable`
                Function fit to the data.
            """
            centers = pfsConfig.extractCenters(fiberIdList)
            return self.fit(vectors, errors, masks, centers)

        def apply(self, fit, fiberIdList, pfsConfig):
            """Apply the fit to fibers

            Parameters
            ----------
            fit : `SomePersistable`
                Function fit to the data.
            fiberIdList : iterable of `int` of length ``M``
                Fibers being fit.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Top-end configuration, for getting the fiber centers.

            Returns
            -------
            result : `numpy.ndarray` of shape ``(M, N)``
                Function fit to the data.
            """
            centers = pfsConfig.extractCenters(fiberIdList)
            return func(centers)
