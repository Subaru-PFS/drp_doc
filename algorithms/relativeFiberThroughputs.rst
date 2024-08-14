Relative Fiber Throughputs
==========================

The science mission of PFS demands accurate sky subtraction
in order to detect faint galaxy emission lines near bright sky lines,
which requires accurate and precise relative fiber throughputs.

Because the blank sky is observed by a separate set of fibers
from those recording the science targets,
we need to able to relate the relative signals of fibers across the instrument
and as a function of wavelength:
we need to be able to connect the fluxes measured
in fiber :math:`i` with the fluxes measured in fiber :math:`j`,
despite the fact that the photons come from different parts of the sky,
pass through different fibers,
different spectrographs
and are measured by different detectors.
We also need to be able to connect the fluxes measured for fiber :math:`k`
in the blue, red and NIR arms.

Unfortunately, it has become clear that the relative fiber throughputs vary with time,
with large changes occurring between observing runs
as the fiber connectors are unplugged and re-plugged,
and smaller (but still significant) changes occurring within a run
and even within a night as forces act on the fiber connectors.


General strategy
----------------

We would strongly prefer to be able to predict the relative fiber throughputs
on the basis of calibration observations taken with high signal-to-noise
at the beginning and end of the night,
and the following strategy reflects this desire.
It may be that reaching our science goals requires adding a more sophisticated approach
(e.g., using the sky lines themselves to monitor the relative fiber throughputs),
but that will require additional research and development.

We use quartz exposures as a reference to connect measured signals
in different fibers, spectrographs and wavelengths.
The quartz provides a single bright light source observed simultaneously
by all fibers and spectrograph cameras.

The measured quartz spectra
(with some corrections applied; see below)
are recorded in the ``fiberProfiles``
as the ``norm`` element of each individual profile.
These normalisation spectra are then propagated to the ``pfsArm.norm`` spectra
when the spectra are extracted,
and these are the basis for the relative fiber throughputs.


Corrections
-----------

The ``pfsArm`` normalisations have two corrections applied to them.

The first attempts to account for the shadow of the black spots on the fibers.
This correction is simplistic and inaccurate,
and we therefore strive to keep fibers out of the shadow of the black spots
in order to avoid adding systematic errors.
The correction is a linear function of the distance of the fiber from the black spot
(which is known to be a poor approximation of the more complicated geometry of the shadows):

.. math::

    c_{\rm bs} & = \textrm{max}(1 - m(r - d), 0) & {\rm if}\ d < r

    c_{\rm bs} & = 1 & {\rm if}\ d \geq\ r

where :math:`m = 1.108` is the slope of the correction (in mm\ :sup:`-1`),
:math:`r = 1.232` is the radius of the black spot shadow (in mm),
and :math:`d` is the distance of the fiber from the center of the black spot (in mm).

The second correction is the screen illumination correction,
which is only applied to exposures that have active lamps
(i.e., not sky exposures),
with the intent of correcting the quartz spectra to look like they come from the sky.
The correction is:

.. math::

    c_{\rm scr} = a x' y' + b x' + c y' + 1

where :math:`a \sim\ -1.6 \times\ 10^{-7}`,
:math:`b \sim\ -8.0 \times\ 10^{-5}`
and :math:`c \sim\ -1.1 \times 10^{-4}`
are the coefficients;
:math:`x'` and :math:`y'` is the position on the focal plane (in mm)
after correcting for the instrument rotator angle.

.. math::

    x' & = x \cos\theta - y \sin\theta \\
    y' & = x \sin\theta + y \cos\theta

where :math:`x` and :math:`y` are the positions on the focal plane (in mm) from the ``pfsConfig``,
and :math:`\theta` is the instrument rotator angle
(from the ``INSROT`` header keyword).

The ``pfsArm.norm`` spectra are therefore:

.. math::

    \tt{pfsArm.norm} = \tt{fiberProfiles.norm} \times c_{\rm bs} \times c_{\rm scr}

Note that the corrections are applied to the ``pfsArm.norm`` rather than ``pfsArm.flux``,
because we want ``pfsArm.flux`` to be identical to the spectra extracted from the image.
The goal is that the ``pfsArm.flux/pfsArm.norm`` values will be
corrected for relative throughput differences.


fiberNorms
----------

The above corrections do not account for the temporal changes in the relative fiber throughputs,
nor any chromatic effects.
This is the purpose of the ``fiberNorms``.

The ``fiberNorms`` are the ratio of the flux of a new quartz in the ``pfsArm.flux``
to the flux of the original reference quartz in the ``pfsArm.norm``.
(Recall that the ``pfsArm.norm`` spectra are from the ``fiberProfiles.norm`` spectra,
which have been corrected for the above effects,
and then the corrections for the new quartz have also been applied to the ``pfsArm.norm`` spectra.)
They are a function of both wavelength and fiber.

Note that the values of the ``fiberNorms`` depend on
the choice of ``fiberProfiles`` used in the spectral extraction.
In order to protect the user against using ``fiberNorms`` that are not appropriate for a given ``pfsArm``,
we record a hash of the ``fiberProfiles`` used for the extractions,
and check that the hashes are consistent.


Measurement
~~~~~~~~~~~

The ``fiberNorms`` are measured from the ``pfsArm`` spectra of quartz exposures:

.. math::

    \tt{fiberNorms} = \tt{pfsArm.flux} / \tt{pfsArm.norm}

Because ``pfsArm.flux`` is the flux of the new quartz,
and ``pfsArm.norm`` is the flux of the original reference quartz
(modulo the above corrections),
the ``fiberNorms`` are the ratio of the flux of the new quartz to the flux of the original reference quartz:

.. math::

    N_{\rm new} & \equiv F_{\rm new} \\
                & = f_{\rm new} / n_{\rm new} \\
                & = f_{\rm new} / ( F_{\rm ref} \, c_{\rm bs,new} \, c_{\rm scr,new}) \\
                & = f_{\rm new} \, c_{\rm bs,ref} \, c_{\rm scr,ref} / ( f_{\rm ref} \, c_{\rm bs,new} \, c_{\rm scr,new}) \\
                & = \frac{f_{\rm new}}{f_{\rm ref}} \times \left( \frac{c_{\rm bs,new} \, c_{\rm scr,new}}{c_{\rm bs,ref} \, c_{\rm scr,ref}} \right)^{-1}

where :math:`N` is the ``fiberNorms``,
:math:`F_{\rm new}` is the normalized flux of the new quartz,
:math:`f_{\rm new}` is the extracted flux of the new quartz,
:math:`n_{\rm new}` is the normalization values of the new quartz,
:math:`c_{\rm bs,new}` is the black spot correction for the new quartz,
:math:`c_{\rm scr,new}` is the screen illumination correction for the new quartz,
and the ``ref`` subscript refers similarly to the reference quartz.

Sometimes the ``pfsArm`` spectra of multiple exposures are combined
before constructing the ``fiberNorms``
in order to increase the signal-to-noise and remove outliers.

Even if there are no changes to the system,
the ``fiberNorms`` values will deviate from a mean value of unity
if the brightness of the quartz lamp changes
or if the exposure time is different.
This feature may be useful for monitoring the stability of the system,
but if it is considered annoying we may remove (and record) the median value to simplify the analysis.

Note that the ``fiberNorms`` only track the relative changes in fiber throughput
between the new quartz and the original reference quartz (contained in the ``fiberProfiles``).
They do not reflect any known changes in the system
(e.g., from re-connecting an MTP)
that are recorded in other ``fiberNorms``.
For this reason, we usually want to divide the new ``fiberNorms``
by another calibration ``fiberNorms`` to see what has changed
that our calibration model does not account for.


Application
~~~~~~~~~~~

The ``fiberNorms`` are applied at the ``mergeArms`` stage,
The goal is that the ``pfsMerged.flux/pfsMerged.norm`` spectra of a quartz
should be identical across fibers and constant as a function of wavelength within the noise.

To apply the ``fiberNorms``,
we multiply the ``pfsArm.norm`` by the ``fiberNorms``:

.. math::

    \tt{pfsArm.norm} \leftarrow \tt{pfsArm.norm} \times \tt{fiberNorms}

The normalized flux of a fiber after merging the arms
(``pfsMerged.flux/pfsMerged.norm``) is:

.. math::

    F_{\rm new} & = f_{\rm new} / n_{\rm new}

The normalization values of the new quartz, :math:`n_{\rm new}`,
is the normalized flux of the reference quartz
multiplied by the various corrections,
including the calibration ``fiberNorms``:

.. math::

    n_{\rm new} & = F_{\rm ref} \times c_{\rm bs,new} \times c_{\rm scr,new} \times N_{\rm cal} \\

where :math:`N_{\rm cal}` is the calibration ``fiberNorms``.

Note that :math:`F_{\rm ref}` has also been corrected for the black spot and screen illumination:

.. math::

    F_{\rm ref} & = f_{\rm ref} / n_{\rm ref} \\
    n_{\rm ref} & = 1 \times c_{\rm bs,ref} \times c_{\rm scr,ref}

When extracted, the normalisation of the reference quartz (:math:`n_{\rm ref}`) is set to unity,
and then the corrections are applied.
Putting everything together, the normalized flux of a quartz exposure after merging the arms is:

.. math::

    F_{\rm new} & = f_{\rm new} / n_{\rm new} \\
                & = f_{\rm new} / ( F_{\rm ref} \, c_{\rm bs,new} \, c_{\rm scr,new} \, N_{\rm cal}) \\
                & = f_{\rm new} \, c_{\rm bs,ref} \, c_{\rm scr,ref} / ( f_{\rm ref} \, c_{\rm bs,new} \, c_{\rm scr,new} \, N_{\rm cal}) \\
                & = \frac{f_{\rm new}}{f_{\rm ref}} \times \left( \frac{c_{\rm bs,new} \, c_{\rm scr,new}}{c_{\rm bs,ref} \, c_{\rm scr,ref}} \right)^{-1} \times N_{\rm cal}^{-1} \\
                & = N_{\rm new} \times N_{\rm cal}^{-1}

If the calibration ``fiberNorms`` used here was constructed from the same quartz exposure
(i.e., ``new`` is the same as ``cal``),
then this expression would simplify to :math:`N_{\rm new} \times N_{\rm cal}^{-1} = 1`,
as expected.

For a science exposure, the screen correction is not applied,
and the equivalent normalised flux is:

.. math::

    F_{\rm sci} & = f_{\rm sci} / n_{\rm sci} \\
                & = \frac{f_{\rm sci}}{f_{\rm ref}} \times \left( \frac{c_{\rm bs,sci}}{c_{\rm bs,ref} \, c_{\rm scr,ref}} \right)^{-1} \times N_{\rm cal}^{-1}

where the ``sci`` subscript refers to the science exposure.

Naming
~~~~~~

Under the current (as of August 2024) Gen2 middleware system,
the ``fiberNorms`` products are named as follows:

- ``fiberNorms``: the ingested calib,
  which is our best guess model for the relative fiber throughputs.
- ``fiberNorms_meas``: the measured relative fiber throughputs,
  which is our best estimate of the actual relative fiber throughputs.

Under the pending (expected September 2024) Gen3 middleware system,
this naming scheme will be changed:

- ``fiberNorms_calib``: the certified calib,
  which is our best guess model for the relative fiber throughputs.
- ``fiberNorms``: the measured relative fiber throughputs,
  which is our best estimate of the actual relative fiber throughputs.

Note the change in the meaning of the ``fiberNorms`` product between the two systems!
