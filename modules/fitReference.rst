.. fitReference:

Flux Reference Fitting
======================

Flux reference fitting is the main algorithmic content of ``calculateReferenceFlux``.
The goal is to fit a physical spectrum to an observed spectrum;
this allows the subsequent flux calibration.

The module will be provided with the spectrum to be fit [#]_,
and should return a reference spectrum.

.. [#] It may also need, either in the constructor or the ``run`` method,
       a data butler for loading the model spectra;
       but if the model spectra is small,
       we could simply place them in one of the git repositories (e.g., ``obs_pfs``).


Here is an example definition::

    class FitReferenceTask(lsst.pipe.base.Task):
        def run(self, spectrum):
            """Fit a physical spectrum to an observed spectrum

            Parameters
            ----------
            spectrum : `pfs.datamodel.PfsSpectrum`
                Spectrum to fit.

            Returns
            -------
            spectrum : `pfs.datamodel.PfsReference`
                Reference spectrum.
            """
            ...
            return spectrum
