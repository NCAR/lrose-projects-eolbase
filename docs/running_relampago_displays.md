# Running the CIDD and Jazz displays for RELAMPAGO

## Introduction

The NCAR-based data for relampago resides on a server at EOL in Boulder.

You can access that data for display purposes, using either CIDD or Jazz.

## Preparation - CIDD

CIDD currently only runs under LINUX, so you will need to install it.

See the [CIDD installation instructions](https://github.com/NCAR/lrose-core/blob/master/docs/build/CIDD_build.linux.md)

## Preparation - Jazz

Jazz is a Java-based display so you will need to install Java 8 (sometimes referred to as 1.8, just be be confusing).

You can either download the java 8 runtime environment from Oracle, or use OpenJdk.

On Linux systems, OpenJdk is sometimes installed automatically.

The Oracle download page is [here](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

The OpenJdk download page is [here](https://openjdk.java.net/install/).

## Download the start scripts

You need the following scripts:

```
  start_CIDD.relampago
  start_Jazz.relampago
```

1. You can download using wget or curl:

```
  wget https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_CIDD.relampago
  wget https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_Jazz.relampago
```

or:

```
  curl https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_CIDD.relampago
  curl https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_Jazz.relampago
```

2. Alternatively you and download the scripts from your browser:

```
  https://github.com/NCAR/lrose-projects-eolbase/tree/master/projDir/display/scripts/start_CIDD.relampago
```

```
  https://github.com/NCAR/lrose-projects-eolbase/tree/master/projDir/display/scripts/start_Jazz.relampago
```

To perform the download correctly, you need to click the 'Raw' button first (top right), and then right-click to get 'Save-as' or equivalent. This will download the script as a text file rather than html, which is what you need.

3. Make the start scripts executable:

```
  chmod +x start_CIDD.relampago
  chmod +x start_Jazz.relampago
```

## Running CIDD:

1. Make sure you have CIDD in your path. Check this with:

```
  which CIDD
```

2. Run the start script:

```
  ./start_CIDD.relampago
```

## Running Jazz

1. Make sure you have java installed. Check this with:

```
  which java
  which javaws
```

2. Run it:

```
  ./start_Jazz.relampago
```

BTW - in Jazz, if you go to 'Realtime' (i.e. the current time) using the time controller at the bottom, you will need to click on a time in the time slider in order to prompt Jazz to retrieve the data.


