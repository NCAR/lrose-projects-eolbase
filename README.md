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

## Account

On each server we have an ```rsfdata``` account.

All data management should be performed under this account.

The eolbase project params and scripts reside under:

```
  ~/git/lrose-projects-eolbase
```

On each server, you will find the links:

```
  ~/.cshrc -> projDir/system/dotfiles/cshrc
  ~/projDir -> git/lrose-projects-eolbase/projDir
  ~/projDir/data -> data directory
  ~/projDir/logs -> logs directory
```

```projDir``` is the top level entry point into the scripts and parameters for the project.

If you want to modify the ```.cshrc``` file, do this down in the projDir tree, and check it in.

## Project directory layout

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

In most subdirectory, you will find:

| SubDir name | Purpose |
|:-------------- |:------------- |
| params | Parameter files |
| scripts | Scripts for starting processes etc. |

## System level scripts and parameters

The system-level scripts reside in:

```
  ~/projDir/system/scripts
```

These are the main controlling scripts for the project.

All of these ```scripts``` directories are included in the PATH. Therefore if you add a script, and run ```rehash```, that script will be available for use.

Executables and other high level scripts will reside in:

```
  ~/lrose/bin
```

The system-level parameters reside in:

```
  ~/projDir/system/params
```

and this directory includes the following link:

```
  ~/projDir/system/params/project_info
```

which points to the relevation project info for that host.

## Controlling the processes running on a host

### Processes that run all the time

The process list for each host is found in:

```
  ~/projDir/control/proc_list
```

This is a link which points to the process list for the host.

The process list looks something like this:

```
######################################################################
# EOLBASE - on hail
######################################################################
# SYSTEM processes
Janitor             logs     start_Janitor.logs        snuff_inst
Scout               primary  start_Scout               kill_Scout
DataMapper          primary  start_DataMapper          kill_DataMapper
######################################################################
# SERVER processes
DsServerMgr         primary  start_inst(no-params)     snuff_inst
DsProxyServer       primary  start_inst(no-params)     snuff_inst
DsMdvServer         manager  start_inst(no-params)     snuff_inst
######################################################################
# Base observations ingest - from LDM
InputWatcher        mrms_conus_plus    start_inst(ingest)  snuff_inst 
Metar2Spdb          ops                start_inst(ingest)  snuff_inst 
LdmDynamic2Static   metar              start_inst(ingest)  snuff_inst
######################################################################
# Interpolate surface data
SurfInterp          ops                start_inst(alg)     snuff_inst
# etc. etc.
######################################################################
```

The 4 columns are as follows:

* Column 1: name of application or script to run
* Column 2: instance of the process
* Column 3: start script for the process
* Column 4: kill script for the process

The start and kill scripts can be actuall script names.

Alternatively they may be macros as follows:

* start_inst(dir): starts the specified application, using the parameter file ```appname.instance``` in the directory ```dir```.
* start_inst(no-params): starts the specified application, without specifying a parameter file
* snuff_inst: kills ```appname.instance```.

### Processes that run at given times - controlled by ```cron```

The cron table for each host is found in:

```
  ~/projDir/control/crontab
```

This is a link which points to the cron table for the host.

These are standard cron tables.

See [geeksforgeeks](https://www.geeksforgeeks.org/crontab-in-linux-with-examples/) for examples.

There are many web pages on writing cron tables.

## Starting and stopping the system

To start the system, run ```start_all```.

This will run ```~/projDir/system/scripts/start_all```.

```start_all``` will in turn do the following:

* start the process mapper: ```procmap```.
* start all of the processes in ```proc_list``` by running ```procmap_list_start```.
* start the auto-restarter: ```procmap_auto_restart```.
* install the cron table by running ```install_crontab```.

```procmap_list_start``` goes through all of the processes in ```proc_list``` and runs their start scipts.

The process_mapper ```procmap``` keeps a registry of all running processes.

All processes listed in the ```proc_list``` register with ```procmap```, generally once every 60 secons.

```procmap_auto_restart``` periodically checks with ```procmap``` to see which processes are running. It checks this against ```proc_list```, and if necessary restarts any missing processes.

To see what is running, type ```ppm```. This is an alias for ```print_procmap -hb -up -status```.

To see what processes are missing, run ```pcheck```. This is an alias for ```procmap_list_check -proc_list $PROJ_DIR/control/proc_list```.

## Keeping track of the data

The main environment variable for the data tree is $DATA_DIR. All data is stored relative to this location.

The ```DataMapper``` process keeps a registry of all data sets stored on the host.

Processes which write data generally register with the ```DataMapper``` after each write.

In addition the ```Scout``` process crawls the tree below $DATA_DIR, accumulating stats on the files and bytes used.

To see the data list type ```pdm```. This is an alias for ```PrintDataMap -all -relt -lreg```.

## Adding a process to the proc_list



As an example, we will use the script that rsync's GPS data results from Potsdam to mpd backups on our servers.

## Adding a script, running under cron, to the EOLBASE project

As an example, we will use the script that rsync's GPS data results from Potsdam to mpd backups on our servers.

