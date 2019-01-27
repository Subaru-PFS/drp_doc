##########################
Release management in JIRA
##########################

Doc Code: PFS-DRP-PRU030003-01

Date: 2019-01-27

Introduction
============

This document describes the current approach for managing releases for DRP-related software in Jira.


Project-level release management
================================

This section describes how releases at the Jira project level (for example the 2D Simulator and 2D DRP) are managed.

Principal Release Tracking Mechanism: labels
--------------------------------------------

For tracking issues related to a release, a label will be introduced marking that release (eg '2DDRP-V5'). 
Individual issues associated with that release will have this label included in the 'label' field for that release.  
The association will be done by typically by management, or by individual developers with management approval.

This approach allows for simple and sophisticated queries to be performed, and enables agile boards to be created for agile development of releases.


Additional tracking mechanism: top-level issue
----------------------------------------------

The above approach provides flexibility, but perhaps not convienient for casual users or managers who are more used to viewing JIRA information at the issue level. 
To this end, an additional mechanism is introduced for simplicity, which is also the approach adopted by the HSC and LSST teams. 
Essentially there will be a single top-level issue identifying the release (described as the 'project release-ticket' in subsequent discussions).
In this issue, the name of the release and general description of the release will be provided 
(although the description may need to be brief given that the content of release can change rapidly especially in the initial stages of project development).

Individual tasks that need to be addressed in that release will be linked to that release as reference issues. 
The link type should be 'is blocked by ', such that the release issue is blocked by the individual tasks. 
This helps indicate that a release cannot be made until those individual tasks are implemented, 
or a management decision is made to move one or more tasks to a later release, or revise those tasks entirely.


Cross-project release management
================================

Occasionally a release of a specific project needs to be made in parallel with a related project. 
For example, the introduction of the NIR arm requires updates to both the 2D simulator and the 2D DRP pipeline, 
which in turn necessitates a release of the 2D simulator at the same time as a release of the 2D DRP pipeline.

The project-level labels described above already allow cross-project queries to be performed (eg 'labels in (2DDRP-V5, SIM2D-V5)'). 

In addition, for simplicity, a cross-project ticket will also be introduced, that includes a link to the release-tickets for the individual projects. 
This ticket itself needs to be included in a particular project, so presently that ticket will be added to the main project, 
which will be in general 'PIPE2D' as that is the project for which the main work in this area will be done.

With this approach, a simple query can be performed, or a single issue can be viewed and the issues therein, to identify tasks and progress required for cross-project releases.


