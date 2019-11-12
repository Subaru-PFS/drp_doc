.. _features:

Features of the Simulator
=========================

The Simulator combines the following elements:

* Object spectra
* Transmission curve
* Optical model
* Dark frames


Object spectra
--------------

At the present time, object spectra are a constant :math:`F_\nu` of 22 mag.
Arc spectra have zero continuum, with discrete lines at
the wavelengths in the line list.
Flux calibration spectra have a modestly sloped continuum spectrum.
Other kinds of spectra are available in the ``SpectrumLibrary``
(and in particular, spectra read from a file),
but selecting them requires fiddling with the code.
Input object spectrum fluxes are in nJy at the top of the atmosphere,
and wavelengths are in nm.

Sky spectrum
^^^^^^^^^^^^

For simulations requiring a sky spectrum, a single realization is provided,
with no variation over the field.
The spectrum is based on no moon and an airmass of 1.3,
corresponding to the expected conditions at the
Mauna Kea summit. See section 3.2.3 of the `PFS Expected Performance Document 
<https://sumire.pbworks.com/w/file/fetch/129441444/PFS-GEN-IPM003001-01_pfs_expected_performance_KYabe_20170731.pdf>`_
for more information on the characteristics of the sky spectrum.

Transmission curve
------------------

We apply a transmission curve that includes
contributions from the atmosphere, telescope and instrument
(including the dichroics and detectors).


Optical model
-------------

The optical model provides a set of oversampled spot images
as a function of fiber and discrete wavelength.
We spline these together and multiply by the input spectrum
to generate a :math:`5\times` oversampled image
before binning down to the native instrument pixel scale.


Dark frames
-----------

We add example dark frames (which include cosmic rays) to the image
to simulate the detector read out process.


Additional features/restrictions
--------------------------------

At the present time, the simulator can model the Blue and Red arms,
but *not* the NIR arm. This planned in future releases.
