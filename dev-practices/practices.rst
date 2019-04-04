Introduction
============

This document provides information as to best practices for a software developer working on the 2D Data Reduction Pipeline software.

In general, we expect PFS DRP development to follow effectively the same
development workflow and coding standards as LSST Data Management. Refer to
the `LSST Developer Guide`_ in conjunction with the notes below.

.. _LSST Developer Guide: https://developer.lsst.io/

PFS Code Repositories
=====================

All the PFS-specific code is hosted in the `Subaru-PFS`_ organization on
`GitHub`_. You will need to be added to the appropriate team (presumably
“princeton”) by the PFS Project Office. Refer to the `pfs_ipmu_jp account
policy`_, then provide `pfsprojectoffice@ipmu.jp`_ with the details they
request.

Relevant packages for 2D DRP development include:

- `datamodel <http://github.com/Subaru-PFS/datamodel>`_: data model definition.
- `obs_pfs <http://github.com/Subaru-PFS/obs_pfs>`_: interface package for I/O.
- `drp_stella <http://github.com/Subaru-PFS/drp_stella>`_: algorithms for 2D spectra reduction.
- `drp_stella_data <http://github.com/Subaru-PFS/drp_stella_data>`_: test data.
- `pfs_pipe2d <http://github.com/Subaru-PFS/pfs_pipe2d>`_: 2D pipeline build and test scripts.

.. _Subaru-PFS: https://github.com/Subaru-PFS/
.. _GitHub: https://github.com/
.. _pfs_ipmu_jp account policy: http://sumire.pbworks.com/w/page/84391630/pfs_ipmu_jp%20account%20policy#Technicalteammember
.. _pfsprojectoffice@ipmu.jp: mailto:pfsprojectoffice@ipmu.jp

Relationship to LSST Development
================================

The PFS DRP code is built on top of the LSST software stack.

Versioning and Installation
---------------------------

LSST follows a six-monthly release cycle. 
Thus, version 17 was released in early 2019, 
and version 18 will follow during the summer of 2019, etc.

PFS development will target a recent stable version of the LSST
stack. It should *not* be necessary to install an unstable snapshot of the
LSST codebase in order to compile, use and develop the PFS code.

Instructions for installing the LSST stack are available from the `LSST
Science Pipelines`_ site. The LSST software is made available through various
distribution channels. Where possible, you are encouraged to use a binary
installation (e.g. eups packages) rather than building from source.

On occasion, PFS work may absolutely require a newer version of an LSST
provided package than is available in an LSST release. In that case, it should
be possible to clone just that individual package from its git repository and
to set it up to work with the release stack.

Any problems arising from interoperability with the LSST stack should be
ticketed in `JIRA`_.

.. _LSST Science Pipelines: https://pipelines.lsst.io/

Development on LSST
-------------------

Occasionally, it may be necessary to suggest modifications, improvements or
fixes to the LSST codebase as a part of PFS development. Follow the normal
LSST procedures (per their Developer Guide, linked above) for this. This may
require for example obtaining an account on LSST's JIRA.

Coding Standards
================

Follow the LSST DM Style Guides for `C++`_ and `Python`_. In general, follow
LSST's guidelines on use of external libraries (`Boost`_, `Astropy`_, etc). We
specifically except the use of `Eigen's unsupported modules`_ from this
policy: their use is specifically permitted.

.. _C++: https://developer.lsst.io/cpp/style.html
.. _Python: https://developer.lsst.io/python/style.html
.. _Boost: https://developer.lsst.io/cpp/boost.html
.. _Astropy: https://developer.lsst.io/python/astropy.html
.. _Eigen's unsupported modules: https://developer.lsst.io/cpp/eigen.html


.. _dev-ci:

Development Workflow
====================

Our development workflow is closely based on LSST. Refer to `their
documentation`_ for details.

In particular, note the following:

.. _sec-jira:

JIRA
----

All work should be ticketed using `PFS JIRA`_ (*not* LSST's JIRA) before it is
undertaken.

When filing JIRA tickets, add them to the correct `JIRA project`_ (click on
the project titles on that list for further information on each project).

The summary and description fields are the most important; 
provide as much information as possible in the description field 
such that an assigned developer can address the issue quickly, 
and provide a meaningful summary such that the issue can be easily identified on a board or query output.

With regards to issue types, we do not make semantic distinctions between "story" and "task", 
both of which reflect a new item of work that needs to be addressed, but "bug" should be used when a problem 
is found in an existing version of a given piece of code.

Sometimes issues need to be grouped into particular categories in order to more easily identify groups of work, 
such as "2D PSF modelling" or "arm merging". 
For this purpose, the "label" field can be used. 
Regarding other exotic fields, the "component" field is typically used for categories that exist in the long term, 
but has its own limitations in that it is project-specific. 
In general, as labels are more flexible it is not recommended to use components.
For short-term work, the developer may use the "epic" field, 
as it does have the advantage that JIRA highlights issues associated to a given epic in scrum boards, 
but it also has a significant limitation in that only one epic can be assigned to one ticket. 
Because of that, this field will not be used for general project scheduling.

In general, developers are encouraged to file issues. But please check existing open issues 
in case the problem or activity has already been addressed,
 and where appropriate, your manager, before filing.

The normal progression of issue status is “Open” (for a freshly created
issue), to “In progress”, to “In Review”, to “Reviewed”, to “Done” (when a
issue has been completed). At any point, an issue can also be set to “Won't
Fix”.


.. _their documentation: https://developer.lsst.io/work/flow.html
.. _PFS JIRA: https://pfspipe.ipmu.jp/jira
.. _JIRA project: https://pfspipe.ipmu.jp/jira/secure/BrowseProjects.jspa#all

Workflow
--------

When the assignee starts work on a given "Open" issue, the issue status should be moved to "In progress". 
This will help managers and stakeholders know which issues are currently being
addressed. Then, a corresponding 'ticket branch' should be created. 
This is a git branch with the name ``tickets/<jira-id>``, 
where ``<jira-id>`` is the name of the JIRA ticket that is being worked on. 
For example, when working on ticket "INFRA-26", the branch ``tickets/INFRA-26`` 
should be created in each of the repositories which are affected. 
Having this convention helps team members see which branches are related to formal activities, 
and which JIRA tickets track those activities, as opposed to informal development.

While making your changes, it is highly recommended to include, or update, unit tests or the integration test 
to demonstrate that the updated code behaves as expected according to the issue description. 
Please also provide or update documentation where appropriate so that users are aware of the change.

Developers *must* ensure that all unit tests pass before merging code. Reviewers and
developers are both responsible for checking this.

When work has been completed, please use ``git rebase -i`` to reorganize commits into logical units. 
Ensure that all unit tests and the integration test pass. 
Then create a GitHub Pull Request and name one or more reviewers. 
The pull request will trigger the continuous integration build. Check that the build has passed.
Then finally set the issue status to “In Review” and assign the same reviewers to the issue as with the pull request.

Please be aware that reviewers may be extremely busy so may not be able to review the issue immediately. 
However, having a significant amount of code in branches pending to be merged for a long period of time is also problematic, 
so to remedy such situations the developer should allow a maximum of 7 working days for the reviewer to take action. 
During that period, please take every reasonable opportunity to prompt the reviewer such that a timely review can be undergone. 
After that period, if the reviewer has not taken any action, the developer may merge the code with no review.
Please add a comment to the JIRA ticket indicating that action has been taken as such.

Otherwise, if the changes are under active review, do not merge to the ``master`` branch until the reviewer is satisfied with the
work. It is not required to agree with or implement every suggestion the
reviewer makes, but when disagreeing, make this clear and iterate with the
reviewer to a solution you are both happy with.

Before merging, again check that all unit tests, integration tests and continuous integration builds pass. 
Please use ``git rebase`` to re-write history for clarity.
Refer to the `LSST guidelines`_ .

When merging to ``master``, use the ``--no-ff`` option to git to generate a
merge commit.

For issues that do not involve changes to deployed code, review is optional:
please use your discretion as to whether a second pair of eyes would help
ensure that the work has been done properly.

.. _LSST guidelines: https://developer.lsst.io/work/flow.html#git-commit-organization-best-practices


Integration Tests
=================

An integration test is available in the `pfs_pipe2d`_ package. This exercises the actual commands users will employ to reduce data, 
ensuring that the individual packages work together as expected.

You can run the integration test using :file:`pfs_integration_test.sh` on the command-line. Note that this
command only runs the integration test, and does *not* build or install the code. It is the user's
responsibility to set up the environment (e.g., sourcing the appropriate :file:`pfs_setups.sh` file; see
:ref:`user-script-install`), including the packages to be tested.

Unless you've modified the ``drp_stella_data`` package as part of your work (in which case you need to use
the ``-b <BRANCH>`` flag), the only argument you need is the directory under which to operate. For example::

  /path/to/pfs_pipe2d/bin/pfs_integration_test.sh /data/pfs

The full usage information for :file:`pfs_integration_test.sh` is::

    Exercise the PFS 2D pipeline code

    Usage: /path/to/pfs_pipe2d/bin/pfs_integration_test.sh [-b <BRANCH>] [-r <RERUN>] [-d DIRNAME] [-c CORES] [-n] <PREFIX>

        -b <BRANCH> : branch of drp_stella_data to use
        -r <RERUN> : rerun name to use (default: 'integration')
        -d <DIRNAME> : directory name to give data repo (default: 'INTEGRATION')
        -c <CORES> : number of cores to use (default: 1)
        -n : don't cleanup temporary products
        <PREFIX> : directory under which to operate

.. _pfs_pipe2d: http://github.com/Subaru-PFS/pfs_pipe2d


Continuous Integration
======================

The `pfs_pipe2d`_ package contains scripts for performing Continuous Integration builds, 
which compile and run the unit tests of the individual packages and runs the integration test. 
Such builds should be run before merging any work to the ``master`` branch.
This ensures that the ``master`` branch always works. Timing will vary according to resource availability and
the number of cores used, but the test typically takes about half an hour to run.

The test can be run in one of two ways: on the developer's own system at the command-line, or on `Travis-CI`_.
The Travis-CI method is recommended because it is requires little effort, uses external resources and provides
a visible demonstration to the team that the code works.

.. _Travis-CI: http://travis-ci.org


Travis use
----------

The integration test will run automatically under `Travis-CI`_ when GitHub pull requests are issued for any
of the following repositories:

- pfs_pipe2d
- drp_stella
- drp_stella_data
- obs_pfs
- datamodel

After issuing a pull request, all you need to do is wait for the test to finish successfully. You'll see a
yellow circle while the test runs. You click on the "Details" button to see the build output. If it
finished successfully, you'll get a green circle and the statement "All checks have passed". Then you're
clear to merge after review. If the Travis check fails, you'll get a red circle, which signals that you need
to fix your contribution. In that case, have a look at the Travis log for clues as to what the problem might
be.

As you push new commits to the pull request, Travis will automatically trigger new integration tests. Because
Travis is triggered on GitHub pull requests, you should ensure you have pushed your work on a common ticket
branch to all appropriate repos before making pull requests. If you want to signal Travis `not to
automatically test a commit`_, add the text ``[ci skip]`` to your commit message.

Unfortunately, due to Travis resource limitations, only 4 MB of logs can be generated. We therefore trap the
build and test output and display only the last 100 lines when the process completes. If this makes it
difficult to determine what's causing your build to fail, you can always run the integration test on the
command-line of your own system.

.. _Travis-CI: http://travis-ci.org
.. _not to automatically test a commit: http://docs.travis-ci.com/user/customizing-the-build#Skipping-a-build

Sprint planning
===============

We work in general on a four-week sprint cycle. At the start of the period, we plan the
work to be undertaken during the sprint. At the end, we review what was
achieved and assess if we could do better next time. 
Please update the status of your JIRA issues regularly so it is clear to others the overal status of the sprint.

Sometimes, it may be necessary to carry out work which hasn't been explicitly
assigned to the sprint. However, this should be the exception rather than the
rule. So please think carefully, and where possible discuss it with others, before
plunging in to unscheduled work.