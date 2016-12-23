#! /bin/csh

#===========================================================================
#
# Plot self consistency for PECAN, SPOL, QC
#
#===========================================================================

PlotSelfCon.pecan.py --debug --sc_file $PROJ_DIR/qc/data/pecan/selfcon.spol.qc.txt --cp_file $PROJ_DIR/qc/data/pecan/spol_pecan_CP_analysis_20150528_000553.txt --title "Z Self-consistency analysis - SPOL - PECAN - QC data" --minElev 1.25

