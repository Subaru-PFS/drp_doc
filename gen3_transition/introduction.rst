Introduction
------------

The 2D DRP Gen3 transition is
a project to migrate the 2D data reduction pipeline's use of the LSST middleware
from the second generation (Gen2) to the third generation (Gen3).

The LSST middleware is the middle layer between the data and
the algorithms responsible for processing the data.
It provides a "data butler" that provides interfaces for reading and writing the data,
a "registry" that keeps track of the data products,
and a framework for running algorithms on the data.

The second generation of the LSST middleware ("Gen2") had two important shortcomings:
it did not keep track of what data products were available,
and it did not provide a simple way to parallelize the processing of data.
The third generation of the LSST middleware ("Gen3") is a complete rewrite that addresses these shortcomings.

The LSST software distributions no longer support the Gen2 middleware,
and so access to bug fixes and new features requires transitioning the PFS 2D DRP to Gen3.
This guide attempts to explain the new features of Gen3 and how we will use them in the PFS 2D DRP,
using the `integration test`_ as a tutorial.

.. _integration test: https://github.com/Subaru-PFS/pfs_pipe2d/blob/gen3/bin/pfs_integration_test.sh


Acknowledgements
^^^^^^^^^^^^^^^^

The PFS 2D DRP Gen3 transition has been a big project that has taken a lot of time and effort.
I am grateful to the LSST pipeline development team for their help in understanding the Gen3 middleware,
and how to overcome the peculiar challenges of applying it to the PFS 2D DRP.
I am especially indebted to Jim Bosch, Nate Lust, Tim Jenness and KT Lim
for promptly answering my ignorant questions on Slack with patience and insight,
and to Lee Kelvin for his helpful writeup on using Gen3 for the `MERIAN project`_.

.. _MERIAN project: https://hackmd.io/@lsk/merian
