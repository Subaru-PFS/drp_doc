.. _concerns:

Concerns and/or Future development directions
---------------------------------------------

Here we outline some concerns with the design as presented
that might be remedied in a future version of the pipeline.

``DetectorMap`` and ``FiberTrace``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a degree of overlap between ``DetectorMap`` and ``FiberTrace``:
both track the center of the fibers as a function of row.
This duplication is unnecessary, but is present in the current design for historical reasons.
The functionality of ``FiberTrace`` could be subsumed into ``DetectorMap`` in a future design,
at which point the ``constructFiberTrace.py`` and ``constructDetectorMap.py`` scripts will also be merged.


Bootstrapping the detectorMap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We need to know the detectorMap before we construct it with ``constructDetectorMap.py``,
because it is an input to both ``constructFiberTrace.py`` and ``constructDetectorMap.py``.
This can be done by using an additional calib product specifically for this purpose
(we use ``bootstrapDetectorMap`` in ``constructDetectorMap.py``).


Association of ``DetectorMap`` and ``FiberTrace`` with science exposures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If there is a one-to-one relationship between science exposures and calibration exposures [#]_,
then it may not be convenient to treat
the detectorMap and fiber trace used for science reductions
as calibs.
In that case, the quartz and arc exposures could be inputs to :ref:`reduceExposure` [#]_,
which would first construct the fiber trace and detectorMap
before operating on the science exposure.


.. [#] This might occur if we "replay" the fiber positions used for the science exposures
       at the end of the night in order to take corresponding
       quartz (for the fiber trace) and arcs (for the detectorMap).

.. [#] The appropriate quartz and arc could be identified through
       having the same ``pfsConfigId`` as the raw exposure.

NIR detectors
^^^^^^^^^^^^^

The NIR detectors produce multiple images as they read "up the ramp".
While they should fit into the general flow of the pipeline design as outlined,
the details are not yet clear, e.g.,
how they will be read by the butler,
and what changes to ISR are necessary to support them.
The specification of details is deferred until we get actual NIR data.
