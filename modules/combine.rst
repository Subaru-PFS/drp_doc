.. combine:

Spectra Combination
===================

The combination of spectra is part of both ``mergeArms`` and ``coaddSpectra``:
in ``mergeArms``, we coadd observations of a target taken in the same exposure
that have only a small wavelength overlap (in the dichroics);
while in ``coaddSpectra``, we coadd observations of a target taken in multiple exposures
with substantial wavelength overlap.

Because we're supporting two different use cases with the same code,
we need two separate interfaces.
The usual ``run`` method will be used to support the combination of spectra from the same exposure.
It shall be provided a list of spectra,
a list of keywords for determining the identity of the combined spectra,
and the class to hold the target spectra.
It shall return the combined spectra.
An additional method, ``runSingle`` will be used to support the combination of a single spectrum
from multiple exposures.
This method shall be provided a list of spectra,
a list of the appropriate fiber for the object in each of the spectra,
the class to hold the target spectra,
the identity of the target
and list of observations [#]_.
It shall return the combined spectrum.
Both these methods should call an additional method that does the actual combination.

.. [#] This may also need be provided the flux calibration and one-dimensional sky subtraction as well.


Here is an example definition::

    class CombineTask(lsst.pipe.base.Task):
        """Combine spectra

        This can be done in order to merge arms (where different sensors have
        recorded measurements for the same wavelength, e.g., due to the use of a
        dichroic), or to combine spectra from different exposures. Both currently
        use the same simplistic placeholder algorithm.

        Note
        ----
        This involves resampling in wavelength.
        """
        def run(self, spectraList, identityKeys, SpectraClass):
            """Combine all spectra from the same exposure

            All spectra should have the same fibers, so we simply iterate over the
            fibers, combining each spectrum from that fiber.

            Parameters
            ----------
            spectraList : iterable of `pfs.datamodel.PfsSpectra`
                List of spectra to coadd.
            identityKeys : iterable of `str`
                Keys to select from the input spectra's ``identity`` for the
                combined spectra's ``identity``.
            SpectraClass : `type`, subclass of `pfs.datamodel.PfsSpectra`
                Class to use to hold result.

            Returns
            -------
            result : ``SpectraClass``
                Combined spectra.
            """
            ...
            return SpectraClass(...)

        def runSingle(self, spectraList, fiberId, SpectrumClass, target, observations):
            """Combine a single spectrum from a list of spectra

            Parameters
            ----------
            spectraList : iterable of `pfs.datamodel.PfsSpectra`
                List of spectra that each contains the spectrum to coadd.
            fiberId : iterable of `int`
                The fiber identifier for each of the spectra that specifies which
                spectrum is to be combined.
            SpectrumClass : `type`, subclass of `pfs.datamodel.PfsSpectrum`
                Class to use to hold result.
            target : `pfs.datamodel.TargetData`
                Target of the observations.
            observations : iterable of `pfs.datamodel.TargetObservations`
                List of observations of the target.

            Returns
            -------
            result : ``SpectrumClass``
                Combined spectrum.
            """
            ...
            return SpectrumClass(...)
