.. measureFluxCalibration:

Measure Flux Calibration
========================

Flux calibration measurement is the main algorithmic content of ``fluxCalibrate``.
The goal is to measure and apply the calibration from counts on the detector to physical flux units.

The module will be provided with the arm-merged spectra
and reference spectra for the flux calibration fibers.
A ``PfsConfig`` will also be provided,
from which can be obtained the position of the target on the sky or on the focal plane,
and the intended position on the focal plane.
The module should return a persistable object that represents the fit.

In addition to the usual ``run`` method,
the module's ``Task`` should also implement an ``apply`` method
that takes the result from the ``run`` method and applies it to spectra.
Like the ``run`` method, this also requires a ``PfsConfig``
to get the required information on fiber positions.

Here is an example definition::

    class MeasureFluxCalibrationTask(lsst.pipe.base.Task):
        def run(self, merged, references, pfsConfig):
            """Measure the flux calibration

            Parameters
            ----------
            merged : `pfs.datamodel.drp.PfsMerged`
                Arm-merged spectra.
            references : `dict` mapping `int` to `pfs.datamodel.PfsSimpleSpectrum`
                Reference spectra, indexed by fiber identifier.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Top-end configuration, for getting fiber positions.

            Returns
            -------
            calib : `SomePersistable`
                Flux calibration.
            """
            ...
            return calib

        def apply(self, merged, pfsConfig, calib):
            """Apply the flux calibration

            Parameters
            ----------
            merged : `pfs.datamodel.drp.PfsMerged`
                Arm-merged spectra.
            pfsConfig : `pfs.datamodel.PfsConfig`
                Top-end configuration, for getting fiber positions.
            calib : `SomePersistable`
                Flux calibration.

            Returns
            -------
            results : `list` of `pfs.datamodel.PfsSingle`
                Flux-calibrated object spectra.
            """
            ...
            return results