# lrose-projects-eolbase

Run-time scripts and parameters for the NCAR/EOL/RSF base project.

## Introduction

We have 5 servers in our eolbase data system:

| Server name | Purpose | Comments |
|:-------------- |:------------- | :------------- |
| eldora | MPD live ingest and data storage | Will be retired soon, replaced by fog |
| fog | MPD live ingest and data storage | Will take over from eldora |
| hail | Live data ingest except for MPD | Also hosts /scr/sci |
| rain | Data storage and processing server | SPOL and CP2 legacy projects |
| snow | Data storage and processing server | pecan, relampago, airborne projects |

## ACCOUNT

On each server we have an 'rsfdata' account.

All data management should be performed under this account.

The eolbase project params and scripts reside under:

```
  ~/git/lrose-projects-eolbase
```

On each server, you will find the links:

```
  ~/projDir -> git/lrose-projects-eolbase/projDir
  ~/.cshrc -> projDir/system/dotfiles/cshrc
```

```projDir``` is the top level entry point into the scripts and parameters for the project.

If you want to modify the ```.cshrc``` file, do this down in the projDir tree, and check it in.

## PROJECT DIRECTORY LAYOUT

| Directory name | Purpose |
|:-------------- |:------------- |
| alg | Algorithms - e.g. PID, TITAN |
| beamBlock | Running RadxBeamBlock |
| cal | Calibration |
| catalog | Creating images for the catalog |
| control | Controlling what runs |
| data | A link to the data directory |
| dial | MPD |
| display | HawkEye, CIDD, Jazz |
| docs | Documentation |
| ingest | Reading in data, reformatting etc. |
| logs | log files |
| qc | QC operations |
| qpe | For example RadxRate, RadxQpe |
| system | System scripts and parameters |

In each subdirectory, you will find:

| SubDir name | Purpose |
|:-------------- |:------------- |
| params | Parameter files |
| scripts | Scripts for starting processes etc. |

## Adding a script, running under cron, to the EOLBASE project

As an example, we will use the script that rsync's GPS data results from Potsdam to mpd backups on our servers.

