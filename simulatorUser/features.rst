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
The sky spectrum has a single realisation, with no variation over the field.
Arc spectra have zero continuum, with discrete lines at the wavelengths in the line list.
Flux calibration spectra have a modestly sloped continuum spectrum.
Other kinds of spectra are available in the ``SpectrumLibrary``
(and in particular, spectra read from a file),
but selecting them requires fiddling with the code.
Input object spectrum fluxes are in nJy at the top of the atmosphere,
and wavelengths are in nm.


Transmission curve
------------------

We apply a transmission curve that includes
contributions from the atmosphere, telescope and instrument
(including the dichroics and detectors).


Optical model
-------------

The optical model provides a set of oversampled spot images as a function of fiber and discrete wavelength.
We spline these together and multiply by the input spectrum
to generate a :math:`5\times` oversampled image
before binning down to the native instrument pixel scale.


Dark frames
-----------

We add example dark frames (which include cosmic rays) to the image
to simulate the detector read out proceess.