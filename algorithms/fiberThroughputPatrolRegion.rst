.. _thetaphi:

Fiber throughput across the patrol region
=========================================

A fiber's throughput depends on where its cobra puts it.
As a cobra moves, its fiber bends and twists, and the light falling on the fiber's face changes;
relative to its value with the cobra at home,
a fiber's throughput varies smoothly by about 1% rms over its patrol region,
and on top of that each fiber has its own fine structure of about 0.2%.

The fiber normalizations (``fiberNorms``) are measured with the cobras at home,
so every spectrum taken with a cobra anywhere else needs a correction.
This chapter describes:

* the smooth model of each fiber's throughput as a function of the cobra's angles (:ref:`thetaphi-smooth`);
* each fiber's fine structure, a layer on top of it (:ref:`thetaphi-fine`);
* how the corrections get into the spectra, and how to make, read and change them
  (:ref:`thetaphi-into-spectra`, :ref:`thetaphi-running`).

The corrections replace ``skyNorms_calib`` entirely,
and the edge-vignetting and per-fiber terms of ``PfiCorrectionTask``.

.. note::

   The data products and their python classes exist (datamodel, PIPE2D-2021).
   Applying them in ``reduceExposure`` is part of the same ticket but not yet written;
   the names of its configuration fields below are provisional.


Conventions
-----------

**The reference.**
The throughput of a fiber is defined relative to its throughput with the cobra at home,
looking at the screen, with the instrument rotator at 0:
that is where the ``fiberNorms`` are measured.
We need to know how it varies over the patrol region, on the sky,
but there is no separate model of the screen:
only the product of the screen and the fiber matters.

**Angles.**
Cobra angles are in degrees, measured from the counter-clockwise hard stops,
as in the cobra calibration, the FPS and the ``pfsConfig``:
:math:`\theta` from ``tht0`` and :math:`\phi` from ``phiIn``.
Home, the clockwise :math:`\theta` stop, is at :math:`360 + (\mathrm{tht1} - \mathrm{tht0}) \bmod 360`,
i.e. at 360–400°, and :math:`\phi = 0`.
:math:`\theta` and :math:`\theta + 360°` put the fiber in the same place.

**Factors and deviations.**
The corrections are multiplicative:
each is a factor by which the norm of a spectrum is multiplied (1 means no correction).
The models are written as deviations (the factor minus 1), as fractions.

**cobraHome.**
A cobraHome exposure has both arms driven to their hard stops.
In that state the fiber's throughput is not the smooth surface's value at home:
it differs from it by a per-fiber offset, :math:`\delta`
(about 0.6% rms over the fibers),
and the fiber sits 60–70 µm off where its angles would put it.
So a cobraHome exposure is recognised by what the FPS did,
not by the angles in the ``pfsConfig``:
its ``cobraCommand`` is ``HOME_BOTH``
(`DAMD-200 <https://pfs-jira.naoj.org/jira/browse/DAMD-200>`_);
for older ``pfsConfig`` files, whose ``HOME`` doesn't say which arm went home,
it is ``HOME`` with :math:`\theta` at its home angle and :math:`\phi = 0`.


Products
--------

.. list-table::
   :header-rows: 1
   :widths: 20 12 20 48

   * - Dataset
     - Status
     - Class
     - Contents
   * - ``thetaPhiModel_calib``
     - Current (input)
     - :py:class:`~pfs.datamodel.PfsThetaPhiModel`
     - The smooth model of every fiber's throughput against the cobra angles,
       with :math:`\delta` for each run and :math:`\alpha` for each arm (:ref:`thetaphi-smooth`).
       One file for the whole PFI;
       a calibration, read by ``reduceExposure``. [#format]_
   * - ``thetaPhiFine_calib``
     - Current (input)
     - :py:class:`~pfs.datamodel.PfsThetaPhiFine`
     - Each fiber's fine structure, for one arm (:ref:`thetaphi-fine`);
       a calibration, read by ``reduceExposure``. [#format]_
   * - ``thetaPhiFineQa``
     - QA [#qa]_
     - :py:class:`~pfs.datamodel.ThetaPhiFineQa`
     - The training data of a fine layer, and its leave-one-night-out predictions.
   * - ``skyNorms``
     - Current
     - ``ConstantPerFiber``
     - Each fiber's throughput measured from the sky in one visit, relative to the ``fiberNorms`` alone:
       the raw data for testing and updating these models.
   * - ``skyNorms_calib``
     - Deprecated [#deprecated]_
     - ``ConstantPerFiber``
     - A combination of skyNorms; replaced by the two calibrations above.

.. [#format] Described in the datamodel (``datamodel.txt``,
   "Fiber throughput across the patrol region").
.. [#qa] Only needed for QA: nothing in the pipeline reads it.
.. [#deprecated] An early attempt to measure the fibers' throughput on the sky,
   applied whatever the cobras' positions; no longer applied.

The calibrations are inputs: you don't need to read them to use the spectra.
``reduceExposure`` looks them up and applies them,
and records in each ``pfsArm`` what it applied (:ref:`thetaphi-into-spectra`).


.. _thetaphi-into-spectra:

How the corrections get into the spectra
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each fiber of an exposure, ``reduceExposure`` reads the cobra's angles
and ``cobraCommand`` from the ``pfsConfig``, and multiplies the fiber's norm by

.. math::

   \mathrm{corrThetaPhi} \times \mathrm{corrFine} =
   \frac{1 + \alpha_\mathrm{arm}\, s(\theta, \phi)}{1 + \delta_\mathrm{run}} \times \bigl(1 + f(\theta, \phi)\bigr)

where :math:`s` is the smooth model, :math:`\delta_\mathrm{run}` the cobraHome offset for the exposure's run,
:math:`\alpha_\mathrm{arm}` the share of :math:`s` that the sky sees, and :math:`f` the fine layer.
For a cobraHome exposure both factors are 1, as the ``fiberNorms`` were measured in that state.
A fiber with no usable smooth model gets no correction (and is flagged);
a fiber with no fine layer gets only the smooth one.

:math:`\delta_\mathrm{run}` is that of the latest run with a measured :math:`\delta`
that started on or before the exposure (``PfsThetaPhiModel.getRun``):
a run without scans uses the previous run's.

What was applied is recorded in the ``pfsArm``'s ``NOTES``:
the product of everything applied to the norm, minus 1, is ``pfiCorrection``
(as before, ``NORM *= 1 + pfiCorrection``);
the black-spot correction is applied and recorded separately (``blackSpotCorrection``).
``MeasureSkyNormsTask`` removes both before measuring,
so ``skyNorms`` stay relative to the ``fiberNorms`` alone,
whatever corrections a reduction applied.
(A later ticket, `PIPE2D-2009 <https://pfs-jira.naoj.org/jira/browse/PIPE2D-2009>`_,
records each term separately, with a version number for the model.)


.. _thetaphi-smooth:

The smooth model
----------------

The model
^^^^^^^^^

For each fiber the flux at cobra angles :math:`(\theta, \phi)` is modelled as

.. math::

   \mathrm{flux}(\theta, \phi) = h\,\bigl(1 + s(\theta, \phi)\bigr) \quad
   [\times (1 + \delta_\mathrm{run}) \text{ for a cobraHome exposure}]

where :math:`h` is a level for each night (a nuisance parameter), and

.. math::

   s(\theta, \phi) = \sum_k c_k \bigl[b_k(\theta, \phi) - b_k(\theta_\mathrm{home}, \phi_\mathrm{home})\bigr]

is zero at home.
The basis functions are products :math:`b_k = F_k(m_k \theta)\, G_k(n_k \phi)`
of :math:`\cos`, :math:`\sin` or 1:
all cross terms with :math:`m_k + n_k \le 3` and the pure terms up to the second harmonic,
20 coefficients per fiber.
The file lists the basis explicitly (its ``BASIS`` table),
so a model with a different basis needs no new code.

The coefficients are fitted to quartz exposures taken while the cobras scan their patrol regions
(the theta/phi scans: :math:`\phi` scans at a few :math:`\theta`, and :math:`\theta` scans at a few :math:`\phi`),
with a level for each night and a :math:`\delta` for each run,
fitting :math:`\ln(\mathrm{flux})`, which is linear in the coefficients.
Points closer than 1.2 mm to a black spot are not fitted.

:math:`\delta`
^^^^^^^^^^^^^^

A cobraHome exposure's throughput differs from the smooth surface at home
by :math:`\delta`, about 0.6% rms over the fibers;
it repeats between runs to about 0.14%.
It is the cobraHome state (both arms against their stops), not a feature of the patrol region:
converged positions near home don't share it,
and one test, with :math:`\theta` at its stop but :math:`\phi` converged,
suggests that each stop contributes about half of it.
The ``fiberNorms`` are measured in this state, so every other position is divided by :math:`1 + \delta`.

:math:`\alpha`
^^^^^^^^^^^^^^

The model is measured with quartz light.
The sky sees most but not all of it:
within each fiber, the sky's variation with position is 0.95 (continuum) or 0.89 (sky lines) times the quartz's.
A single :math:`\alpha` per arm is applied to everything;
splitting lines from continuum would need a model of the sky spectrum in the correction.

How well does it work?
^^^^^^^^^^^^^^^^^^^^^^

The model is achromatic to 0.06–0.10% from 420 to 870 nm,
so one model serves every arm.
Two independent fits agree to 0.20% rms, out of a 1.2% signal,
and a model fitted to one run predicts another, months later, to 0.23%.


.. _thetaphi-fine:

Each fiber's fine structure
---------------------------

The physical picture
^^^^^^^^^^^^^^^^^^^^

After the smooth model, each fiber still has structure that repeats when its cobra returns to the same place:
two visits of a fiber at the same position on different nights correlate at about 0.56,
on scales of about 2° and, more broadly, 15–20°.
It is mostly the fiber's own:
a different fiber at the same place on the focal plane shares only 0.2–0.3 of it.
It is stable for months, though it changed during and after Run 26 (2026-01).
The cobras' small bearings, bending the fibers, would explain it.

The model
^^^^^^^^^

For each fiber the layer :math:`f(\theta, \phi)` is a Gaussian process
whose kernel is the sum of two Matérn 3/2 terms,
fine (about 2° in both :math:`\theta` and :math:`\phi`) and broad (about 20° by 15°),
with :math:`\theta` differences wrapped.
It is trained on the sky's residuals from the smooth model,
at converged cobra positions (not cobraHome),
pooled over the runs since the last break.
Its mean anywhere is

.. math::

   f(\theta, \phi) = \sum_i w_i \sum_c A_c^2\, M_{3/2}(r_{ic}), \qquad
   r_{ic} = \sqrt{\left(\frac{\Delta\theta_i}{\ell_{\theta,c}}\right)^2 + \left(\frac{\Delta\phi_i}{\ell_{\phi,c}}\right)^2},
   \qquad M_{3/2}(r) = (1 + \sqrt{3}\,r)\,e^{-\sqrt{3}\,r}

so the file holds each fiber's training points :math:`(\theta_i, \phi_i)` and weights :math:`w_i`
(:math:`(K + N)^{-1} y`), about 700 per fiber.
A layer is made for each arm, and records the smooth model it was fitted against;
it is refused with any other.

**It is the sky's correction, applied to all light.**
Quartz light shares only about a quarter of the sky's fine structure,
so for quartz the correction is wrong by about 0.07% rms (0.10% close to the training points).
It is 1 at home, so the ``fiberNorms`` are unaffected.

How well does it work?
^^^^^^^^^^^^^^^^^^^^^^

Predicting each night of each fiber from its other nights (r, Runs 28–31),
the layer removes about 26% of the per-visit variance of the sky residuals,
and 22% of the variance of each fiber's nightly offset (0.208 → 0.184% rms).
It works where the fiber has been before:
it removes 42% where a training point lies within half a fine length scale,
and 10% where none lies within two (where only the broad term helps).
Its value grows with the number of nights.

Each run, the layer is tested against the new data
(the repeat correlation against the previous run, ``REPEAT_CORR``);
a fiber that fails gets no layer (``NO_LAYER``),
and a low correlation is flagged (``STALE``) as a possible break.
Its error at any position is estimated from the distance to the nearest training point
(``PfsThetaPhiFine.getError``).


.. _thetaphi-running:

Running, reading and changing it
--------------------------------

Making the calibrations
^^^^^^^^^^^^^^^^^^^^^^^

For now the calibrations are written by a script from the analysis code that fits them
(the smooth model from the theta/phi scans; the fine layer from the sky);
a pipeline task to fit them will follow.
They are certified like other calibrations,
the smooth model per epoch (it is stable for at least a year),
and the fine layer per run, with each layer certified alongside the smooth model it was fitted against.

Reading them
^^^^^^^^^^^^

.. code-block:: python

   model = butler.get("thetaPhiModel_calib", instrument="PFS", visit=148258)
   fine = butler.get("thetaPhiFine_calib", instrument="PFS", arm="r", visit=148258)
   fine.checkSmoothModel(model)                     # raises if they don't belong together

   pfsConfig = butler.get("pfsConfig", visit=148258)
   s = model.evaluate(pfsConfig.fiberId, pfsConfig.cobraTheta, pfsConfig.cobraPhi)
   f = fine.evaluate(pfsConfig.fiberId, pfsConfig.cobraTheta, pfsConfig.cobraPhi)

What was applied to a ``pfsArm`` is in its ``NOTES`` (``pfiCorrection``; see above).

Changing them
^^^^^^^^^^^^^

To test a new model on reduced data, remove what was applied and apply the new one:
divide each fiber's norm by :math:`1 + \mathrm{pfiCorrection}`,
then multiply it by the new factors
(``PfsThetaPhiModel.getCorrection`` and ``PfsThetaPhiFine.getCorrection``).
``skyNorms`` need no such step: they are always relative to the ``fiberNorms`` alone.


The objects the butler returns
------------------------------

The file formats are described in the datamodel;
this section describes the python objects.
Angles are in degrees, as in the ``pfsConfig`` (see Conventions);
models and errors are fractions.

.. py:class:: pfs.datamodel.PfsThetaPhiModel

   The smooth model of every fiber in the PFI.

   .. py:method:: evaluate(fiberId, theta, phi) -> numpy.ndarray

      The deviation :math:`s` at :math:`(\theta, \phi)`, vectorised;
      zero at home, NaN for unknown fibers or fibers with no model.

   .. py:method:: getCorrection(fiberId, theta, phi, arm: str, date: str, isCobraHome) -> numpy.ndarray

      The factor :math:`(1 + \alpha_\mathrm{arm} s)/(1 + \delta_\mathrm{run})`,
      1 where ``isCobraHome``, NaN where there's no usable model or no :math:`\delta`.
      ``date`` (ISO-8601) selects the run; ``isCobraHome`` is decided by the caller from ``cobraCommand``.

   .. py:method:: getRun(date: str) -> str | None

      The run whose :math:`\delta` applies on a date.

   .. py:method:: getHomeOffset(fiberId, run: str) -> numpy.ndarray

      :math:`\delta` for a run.

   .. py:method:: isGood(fiberId, badFlags=None) -> numpy.ndarray

      Whether each fiber has a usable model (not ``NO_MODEL`` or ``FIT_FAILED``).

   .. py:attribute:: hash
      :type: int

      A hash of the model, recorded by the fine layers fitted against it.

.. py:class:: pfs.datamodel.PfsThetaPhiFine

   Each fiber's fine structure, for one arm.

   .. py:method:: evaluate(fiberId, theta, phi) -> numpy.ndarray

      The layer :math:`f`; 0 for fibers with no layer.

   .. py:method:: getCorrection(fiberId, theta, phi, isCobraHome) -> numpy.ndarray

      The factor :math:`1 + f`; 1 where ``isCobraHome`` or there's no layer.

   .. py:method:: getError(fiberId, theta, phi) -> numpy.ndarray

      The approximate error in :math:`f`, from the distance to the nearest training point.

   .. py:method:: checkSmoothModel(model: PfsThetaPhiModel) -> None

      Raise if the layer wasn't fitted against ``model``.

.. py:class:: pfs.datamodel.ThetaPhiFineQa

   A table of the layer's training points (``fiberId``, ``visit``, ``night``, ``source``, ``theta``, ``phi``,
   ``y``, ``sigma``, ``used``, ``looPred``).


Known limitations
-----------------

* At :math:`\phi` below about 20°, quartz light shows a component that varies with :math:`\theta`
  and scales with :math:`\delta`, which the sky doesn't.
  The smooth model is fitted to quartz, so for the sky it is off by up to about :math:`0.1\delta` there
  (about 0.06% rms); the fine layer absorbs this where it has data.
  It is not understood, and is being investigated with converged quartz exposures at small :math:`\phi`.
* :math:`\delta` is measured from the quartz scans with :math:`\phi` at its stop near home;
  the sky sees only about 0.8 of it.
* The fine layer helps only where a fiber has been before;
  elsewhere it reverts to zero (its broad term apart).
* For quartz light the fine layer is wrong by about 0.07% rms (it is the sky's correction).
* Until the FPS records ``HOME_BOTH`` (DAMD-200), cobraHome exposures are recognised by
  ``HOME`` together with the angles.
* Until PIPE2D-2009, only the total correction is recorded in a ``pfsArm``, not each term.
