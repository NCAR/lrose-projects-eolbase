/**********************************************************************
 * TDRP params for SunCal
 **********************************************************************/

//======================================================================
//
// SunCal analyses data from tsarchive time series files taken during 
//   sun scans.
//
//======================================================================
 
//======================================================================
//
// DEBUGGING AND PROCESS CONTROL.
//
//======================================================================
 
///////////// debug ///////////////////////////////////
//
// Debug option.
//
// If set, debug messages will be printed appropriately.
//
//
// Type: enum
// Options:
//     DEBUG_OFF
//     DEBUG_NORM
//     DEBUG_VERBOSE
//     DEBUG_EXTRA
//

debug = DEBUG_OFF;

///////////// instance ////////////////////////////////
//
// Process instance.
//
// Used for registration with procmap.
//
//
// Type: string
//

instance = "mascrad.qc";

///////////// register_with_procmap ///////////////////
//
// Option to register with the process mapper.
//
// If true, this application will try to register with procmap once per 
//   minute. (If unable to do so, no error occurs.).
//
//
// Type: boolean
//

register_with_procmap = FALSE;

//======================================================================
//
// DATA INPUT.
//
//======================================================================
 
///////////// input_mode //////////////////////////////
//
// Input mode - files or time series API.
//

//
// TS_FMQ_INPUT: the application will read the time series from a file 
//   message queue and process the pulses as they come in. 
//
// TS_FILE_INPUT: the application will process all the files specified 
//   on the command line. 
//
// TS_REALTIME_DIR_INPUT: the application will watch the input directory 
//   for new files, and will process those files as they arrive. This mode 
//   is suitable for automated operation. 
//
// MOMENTS_REALTIME_INPUT: watch the input directory for new moments 
//   files, and process each volume as it arrives. 
//
// MOMENTS_ARCHIVE_INPUT: will process the moments files in the input 
//   directory, between the start and end times. 
//
// MOMENTS_FILELIST_INPUT: will process the moments files listed on the 
//   command line. .
//
//
// Type: enum
// Options:
//     TS_FILELIST_INPUT
//     TS_FMQ_INPUT
//     TS_REALTIME_DIR_INPUT
//     MOMENTS_REALTIME_INPUT
//     MOMENTS_ARCHIVE_INPUT
//     MOMENTS_FILELIST_INPUT
//

input_mode = TS_FILELIST_INPUT;

///////////// input_fmq_name //////////////////////////
//
// FMQ name. For TS_FMQ_INPUT only.
//
// Path to FMQ files. There are 2 files, one with a .buf extension and 
//   one with a .stat extention. This path does not include the 
//   extensions.
//
//
// Type: string
//

input_fmq_name = "/tmp/fmq/ts";

///////////// input_dir ///////////////////////////////
//
// Directory to watch for incoming files.
//
// Applies to TS_REALTIME_DIR_INPUT mode only. This is the directory 
//   path for sunscan time series files. As files arrive in the directory, 
//   the application will read them in and process them.
//
//
// Type: string
//

input_dir = "/scr/eldora2/rsfdata/firestone/time_series/sband/save";

///////////// archive_start_time //////////////////////
//
// Specify the start time for the files in archive mode.
//
// Format is 'yyyy mm dd hh mm ss'. Applies to MOMENTS_ARCHIVE_INPUT 
//   mode.
//
//
// Type: string
//

archive_start_time = "2012 06 01 00 00 00";

///////////// archive_end_time ////////////////////////
//
// Specify the end time for the files in archive mode.
//
// Format is 'yyyy mm dd hh mm ss'. Applies to MOMENTS_ARCHIVE_INPUT 
//   mode.
//
//
// Type: string
//

archive_end_time = "2012 06 02 00 00 00";

///////////// n_samples ///////////////////////////////
//
// Number of pulse samples in a beam.
//
//
// Type: int
//

n_samples = 128;

///////////// start_gate //////////////////////////////
//
// Start gate for analysis.
//
//
// Type: int
//

start_gate = 700;

///////////// n_gates /////////////////////////////////
//
// Number of gates for analysis.
//
//
// Type: int
//

n_gates = 250;

///////////// alternating_mode ////////////////////////
//
// Does this system transmit alternating H and V pulses.
//
// In some dual-polarization radars, the transmitter toggles between H 
//   and V transmit. Although this does not affect sun measurements 
//   directly, it does affect how the data is handled in the receiver 
//   chain.
//
//
// Type: boolean
//

alternating_mode = TRUE;

///////////// switching_receiver //////////////////////
//
// Does the receiver path switch between each pulse.
//
// In some alternating mode radars, the receiver chain switches between 
//   pulses. This is done to create a co-polar and cross-polar receiver 
//   system which is more stable for ZDR. If this is set to TRUE, then the 
//   receiver is assumed to switch and the data for each channel is 
//   gathered accordingly. NOTE - this only applies in alternating mode.
//
//
// Type: boolean
//

switching_receiver = TRUE;

///////////// invert_hv_flag //////////////////////////
//
// Option to invert H/V flag in pulse data.
//
// Only applies to alternating dual polarization mode. Normally, the HV 
//   flag is set to 1 for H, 0 for V. If the flag in the data has the 
//   opposite sense, set this to true.
//
//
// Type: boolean
//

invert_hv_flag = FALSE;

//======================================================================
//
// FIELD NAMES FOR MOMENTS FILES.
//
// Names of specified fields in the moments files.
//
//======================================================================
 
///////////// moments_field_names /////////////////////
//
//
// Type: struct
//   typedef struct {
//      string DBMHC;
//      string DBMVC;
//      string DBMHX;
//      string DBMVX;
//      string ZDR;
//      string PHIDP;
//      string RHOHV;
//      string NCP;
//      string LAG1_HC_DB;
//      string LAG1_HC_PHASE;
//      string LAG1_VC_DB;
//      string LAG1_VC_PHASE;
//      string RVVHH0_DB;
//      string RVVHH0_PHASE;
//   }
//
//

moments_field_names = {
    DBMHC = "DBMHC",
    DBMVC = "DBMVC",
    DBMHX = "DBMHX",
    DBMVX = "DBMVX",
    ZDR = "ZDR",
    PHIDP = "PHIDP",
    RHOHV = "RHOHV",
    NCP = "NCP",
    LAG1_HC_DB = "LAG1_HC_DB",
    LAG1_HC_PHASE = "LAG1_HC_PHASE",
    LAG1_VC_DB = "LAG1_VC_DB",
    LAG1_VC_PHASE = "LAG1_VC_PHASE",
    RVVHH0_DB = "RVVHH0_DB",
    RVVHH0_PHASE = "RVVHH0_PHASE"
};

//======================================================================
//
// VOLUME IDENTIFICATION OPTIONS.
//
//======================================================================
 
///////////// scan_mode_rhi ///////////////////////////
//
// Scan mode is RHI instead of SECTOR.
//
// Set to TRUE if the scan is in RHI mode and the RHI flag is not set in 
//   the pulse headers.
//
//
// Type: boolean
//

scan_mode_rhi = FALSE;

///////////// analyze_individual_volumes //////////////
//
// Option to identify individual sun volumes for the analysis.
//
// If false, all of the input data will be analyzed together. If true, 
//   the program will identify individual sun scans for analysis by 
//   monitoring the antenna elevation angle for a decrease which indicates 
//   that the volume is restarting. You have the option of including more 
//   than 1 volume in the analysis - see n_volumes_for_analysis.
//
//
// Type: boolean
//

analyze_individual_volumes = TRUE;

///////////// n_volumes_for_analysis //////////////////
//
// Number of consecutive volumes to be combined for each analysis. The 
//   program will go through all of the data grouping the volumes 
//   accordingly.
//
// Applies if analyze_individual_volumes is true.
//
//
// Type: int
//

n_volumes_for_analysis = 1;

///////////// min_n_volumes_for_analysis //////////////
//
// Minimum number of consecutive volumes to be included in the analysis.
//
// The program checks for the number of available volumes. If it exceeds 
//   this number, the analysis is performed. If not, the data will be 
//   ignored.
//
//
// Type: int
//

min_n_volumes_for_analysis = 1;

///////////// min_beams_per_volume ////////////////////
//
// Min number of beams per volume volume.
//
//
// Type: int
//

min_beams_per_volume = 100;

///////////// max_beams_per_volume ////////////////////
//
// Max number of beams per volume volume.
//
//
// Type: int
//

max_beams_per_volume = 20000;

///////////// check_for_elevation_change //////////////
//
// Option to identify end of volumes by elevation change.
//
// If true, the antenna elevation will be checked. If it changes by a 
//   significant amount, an end of volume is likely. See 
//   'elev_change_for_end_of_volume'. If false, the volume number will be 
//   checked for changes.
//
//
// Type: boolean
//

check_for_elevation_change = FALSE;

///////////// elev_change_for_end_of_volume ///////////
//
// Minimum delta elevation to indicate end of volume (deg).
//
// At the end of a volume, the elevation angle will be reset to the 
//   starting angle. When this happens the program can detect the end of 
//   volume by the rapid change in elevation angle. This is the minimum 
//   angular change to signal and end of volume.
//
//
// Type: double
//

elev_change_for_end_of_volume = 2;

///////////// volume_starts_at_bottom /////////////////
//
// Volume starts at lowest elevation angle and moves upwards.
//
// If false, volume starts at top and moves downwards.
//
//
// Type: boolean
//

volume_starts_at_bottom = TRUE;

///////////// max_time_gap_within_volume //////////////
//
// Max time gap within a volume (secs).
//
// If the time between pulses exceeds this value, the current analysis 
//   will be terminated and a new analysis begun.
//
//
// Type: int
//

max_time_gap_within_volume = 60;

///////////// max_pointing_angle_error_deg ////////////
//
// Max error in pointing angle for valid data (deg).
//
// We discard data when the pointing angle differs from the commanded 
//   fixed angle by greater than this amount.
//
//
// Type: double
//

max_pointing_angle_error_deg = 1;

//======================================================================
//
// RADAR NAME AND LOCATION.
//
//======================================================================
 
///////////// radar_name //////////////////////////////
//
// Name of radar.
//
//
// Type: string
//

radar_name = "SPOL";

///////////// radar_site //////////////////////////////
//
// Site of radar.
//
//
// Type: string
//

radar_site = "McCracken";

///////////// get_location_from_data //////////////////
//
// Option to read the latitude and longitude from the time series data.
//
// If false, the values specified in this file will be used.
//
//
// Type: boolean
//

get_location_from_data = TRUE;

///////////// radar_lat ///////////////////////////////
//
// Latitude of radar location (deg).
//
// North is positive, South is negative.
//
//
// Type: double
//

radar_lat = 40.1233;

///////////// radar_lon ///////////////////////////////
//
// Longitude of radar location (deg).
//
// East is positive, West is negative.
//
//
// Type: double
//

radar_lon = -104.891;

///////////// radar_alt_km ////////////////////////////
//
// Altitude of radar (km).
//
//
// Type: double
//

radar_alt_km = 1.55296;

//======================================================================
//
// FIXED TARGET LOCATION.
//
// Optionally you can perform the analysis for a fixed target location, 
//   instead of the moving sun.
//
//======================================================================
 
///////////// specify_fixed_target_location ///////////
//
// Option to analyze the grid based on a fixed target location.
//
// This location is used instead of computing the location of the sun. 
//   This is useful for calibration using a target such as a sphere.
//
//
// Type: boolean
//

specify_fixed_target_location = FALSE;

///////////// target_elevation ////////////////////////
//
// Elevation angle for target (deg).
//
// See 'specify_fixed_target_location'.
//
//
// Type: double
//

target_elevation = 0;

///////////// target_azimuth //////////////////////////
//
// Azimuth angle for target (deg).
//
// See 'specify_fixed_target_location'.
//
//
// Type: double
//

target_azimuth = 0;

//======================================================================
//
// GRID DETAILS.
//
//======================================================================
 
///////////// grid_min_az /////////////////////////////
//
// Min azimiuth for the grid (deg).
//
//
// Type: double
//

grid_min_az = -5;

///////////// grid_max_az /////////////////////////////
//
// Max azimiuth for the grid (deg).
//
//
// Type: double
//

grid_max_az = 5;

///////////// grid_delta_az ///////////////////////////
//
// Resolution of regular grid in azimuth (deg).
//
//
// Type: double
//

grid_delta_az = 0.1;

///////////// grid_min_el /////////////////////////////
//
// Min elevation for the grid (deg).
//
//
// Type: double
//

grid_min_el = -2;

///////////// grid_max_el /////////////////////////////
//
// Max elevation for the grid (deg).
//
//
// Type: double
//

grid_max_el = 2;

///////////// grid_delta_el ///////////////////////////
//
// Resolution of regular grid in elevation (deg).
//
//
// Type: double
//

grid_delta_el = 0.1;

//======================================================================
//
// NOISE CORRECTION.
//
//======================================================================
 
///////////// correct_powers_for_noise ////////////////
//
// Option to subtract noise from powers.
//
// If true, the noise power is subtracted from the received power.
//
//
// Type: boolean
//

correct_powers_for_noise = TRUE;

///////////// noise_method ////////////////////////////
//
// Method for determining the noise, if noise correction is needed.
//
// GET_NOISE_FROM_CAL_FILE: read the noise values from the XML file 
//   specified in the parameter 'cal_xml_file_path'. 
//   GET_NOISE_FROM_TIME_SERIES: some data streams have noise values in 
//   the time series. - e.g. SIGMET tsarchive. COMPUTE_MEAN_NOISE: compute 
//   the mean noise from data which is away from the sun. See 
//   'min_angle_offset_for_noise_power. COMPUTE_MN_NOISE: compute the 
//   minimum noise from data which is away from the sun. See 
//   'min_angle_offset_for_noise_power. .
//
//
// Type: enum
// Options:
//     GET_NOISE_FROM_CAL_FILE
//     GET_NOISE_FROM_TIME_SERIES
//     COMPUTE_MEAN_NOISE
//     COMPUTE_MIN_NOISE
//

noise_method = GET_NOISE_FROM_TIME_SERIES;

///////////// min_angle_offset_for_noise_power ////////
//
// Min angle from sun center for noise power (deg).
//
// The noise will be computed as the mean of power from beams outside 
//   this angular offset.
//
//
// Type: double
//

min_angle_offset_for_noise_power = 2;

///////////// cal_xml_file_path ///////////////////////
//
// Path for XML calibration file.
//
// At a minimum, the calibration file should contain noiseDbm values for 
//   each channel.
//
//
// Type: string
//

cal_xml_file_path = "$(PROJ_DIR)/cal/data/pecan/sband_1.5us.alt/TsCalAuto_20141009_160939.xml";

//======================================================================
//
// INTERFERENCE REMOVAL FOR SUN CENTROID.
//
// Option to set a maximum sun power, so that we can filter out high 
//   power values which affect the computation of the sun centroid.
//
//======================================================================
 
///////////// set_max_sun_power ///////////////////////
//
// Option to set a maximum acceptable power value.
//
// If true, powers above this value will be set to -120 dBm.
//
//
// Type: boolean
//

set_max_sun_power = FALSE;

///////////// max_valid_sun_power_dbm /////////////////
//
// Max valid sun power value (dBm).
//
// See 'set_max_power'.
//
//
// Type: double
//

max_valid_sun_power_dbm = -60;

//======================================================================
//
// COMPUTING CORRELATION OVER THE SUN DISK.
//
//======================================================================
 
///////////// max_solid_angle_for_mean_correlation ////
//
// Solid angle for computing mean correlation over sun disk (deg).
//
// The mean correlation will be computed using grid points within this 
//   angle.
//
//
// Type: double
//

max_solid_angle_for_mean_correlation = 1;

//======================================================================
//
// CROSS-POLAR POWER ANALYSIS.
//
//======================================================================
 
///////////// sun_edge_below_peak_db //////////////////
//
// Power of sun edge relative to the peak (dB).
//
// The sun position is computed using the power at each point. Only 
//   powers within this margin of the peak power are used in the 
//   computations.
//
//
// Type: double
//

sun_edge_below_peak_db = 8;

///////////// n_s1s2_ratios_computed //////////////////
//
// Number of ratios computed for S1S2.
//
// Each ratio is computed for a different solid angle.
//
//
// Type: int
//

n_s1s2_ratios_computed = 8;

///////////// min_solid_angle_for_s1s2 ////////////////
//
// Min solid angle over which to compute S1S2 mean (deg).
//
// This is the min angle for computing S1S2. The angle is centered on 
//   the sun, and the mean ratio is computed over the entire angle. For 
//   example, if set to 1.0, all points in the grid within 0.5 degrees of 
//   the sun centroid will be used.
//
//
// Type: double
//

min_solid_angle_for_s1s2 = 0.25;

///////////// delta_solid_angle_for_s1s2 //////////////
//
// Delta solid angle over which to compute S1S2 mean (deg).
//
// A number of ratios are computed for a range of solid angles. This is 
//   the delta between each solid angle.
//
//
// Type: double
//

delta_solid_angle_for_s1s2 = 0.25;

///////////// solid_angle_for_zdr_bias ////////////////
//
// Solid angle for computing ZDR bias (deg).
//
//
// Type: double
//

solid_angle_for_zdr_bias = 1;

///////////// npoints_power_ranking ///////////////////
//
// Number of grid points used to compute ratios using ranked powers.
//
// In this method, the points in the grids are ranked, and a mean is 
//   computed using the top npoints_power_ranking points, after dropping 
//   the tops few points. See npoints_dropped_ranking.
//
//
// Type: int
//

npoints_power_ranking = 9;

///////////// compute_cross_polar_power_ratio /////////
//
// Option to compute cross polar power ratio from side-lobe clutter.
//
// If true, xpol ratio will be computed using data from specified gates. 
//   This is only applicable in alternating mode with the transmitter 
//   running.
//
//
// Type: boolean
//

compute_cross_polar_power_ratio = TRUE;

///////////// cross_polar_start_gate //////////////////
//
// Start gate for cross-polar analysis.
//
//
// Type: int
//

cross_polar_start_gate = 20;

///////////// cross_polar_n_gates /////////////////////
//
// Number of gates for cross-polar analysis.
//
//
// Type: int
//

cross_polar_n_gates = 250;

///////////// cross_polar_min_snr /////////////////////
//
// Minimum SNR for cross-polar analysis (dB).
//
//
// Type: double
//

cross_polar_min_snr = 10;

///////////// cross_polar_max_snr /////////////////////
//
// Maximum SNR for cross-polar analysis (dB).
//
//
// Type: double
//

cross_polar_max_snr = 60;

///////////// cross_polar_min_valid_ratio_db //////////
//
// Minimum valid Vx/Hx ratio (dB).
//
// Sometimes, odd data leads to inappropriate ratios. This puts limits 
//   on the ratios to be used in the analysis.
//
//
// Type: double
//

cross_polar_min_valid_ratio_db = -2;

///////////// cross_polar_max_valid_ratio_db //////////
//
// Maximum valid Vx/Hx ratio (dB).
//
// Sometimes, odd data leads to inappropriate ratios. This puts limits 
//   on the ratios to be used in the analysis.
//
//
// Type: double
//

cross_polar_max_valid_ratio_db = 2;

///////////// cross_polar_min_rho_vx_hx ///////////////
//
// Minimum valid Vx-Hx correlation (dB).
//
// Sometimes, odd data leads to inappropriate ratios. This sets a 
//   minimum value for the correlation between vx and hx.
//
//
// Type: double
//

cross_polar_min_rho_vx_hx = 0.98;

///////////// min_angle_offset_for_cross_pol_ratio ////
//
// Min angle offset from sun center for cross polar ratio (deg).
//
// The ratio will be computed from beams outside this anglular offset.
//
//
// Type: double
//

min_angle_offset_for_cross_pol_ratio = 0;

//======================================================================
//
// OPTION TO RETRIEVE XPOL RATIO from SPDB.
//
//======================================================================
 
///////////// read_xpol_ratio_from_spdb ///////////////
//
// Option to read the cross-polar ratio from SPDB.
//
// We can compute the x-polar ratio using the AltCpCompute app, which 
//   stores the results in SPDB. So, in addition to computing it from the 
//   sun scan data itself, we can retrieve the results from AltCpCompute 
//   and add that to the output for comparison purposes.
//
//
// Type: boolean
//

read_xpol_ratio_from_spdb = FALSE;

///////////// use_xpol_ratio_from_spdb ////////////////
//
// Option to use the the cross-polar ratio from SPDB instead of that 
//   computed from the solar.
//
// With S1S2 from the solar, and the xpol ratio, we can compute ZDR 
//   bias. This option allows us to use the ratio retrieved from SPDB 
//   instead of the value computed from the solar scan itself.
//
//
// Type: boolean
//

use_xpol_ratio_from_spdb = FALSE;

///////////// xpol_ratio_spdb_url /////////////////////
//
// URL for reading x-polar ratio from SPDB.
//
// See 'get_xpol_ratio_from_spdb'.
//
//
// Type: string
//

xpol_ratio_spdb_url = "mascrad/spdb/cal/zdr/cp_alt";

///////////// xpol_ratio_radar_name ///////////////////
//
// Name of station for xpol ratio data.
//
// If empty, we will use the closest data in time.
//
//
// Type: string
//

xpol_ratio_radar_name = "";

///////////// xpol_ratio_search_margin_secs ///////////
//
// Search margin when finding xpol ratio (secs).
//
// We search for the xpol ratio result closest in time to the radar 
//   volume. This is the search margin on either side of the sunscan time.
//
//
// Type: int
//

xpol_ratio_search_margin_secs = 86400;

//======================================================================
//
// OPTION TO RETRIEVE SITE TEMP from SPDB.
//
//======================================================================
 
///////////// read_site_temp_from_spdb ////////////////
//
// Option to read the site ambient temperature from SPDB.
//
// It can be useful to check for dependency between the solar data, xpol 
//   ratio and temperature. This gives you the option of retrieving the 
//   temperature from SPDB and including it in the analysis.
//
//
// Type: boolean
//

read_site_temp_from_spdb = TRUE;

///////////// site_temp_spdb_url //////////////////////
//
// URL for reading temperature data from SPDB.
//
// See 'get_temperature_from_spdb'.
//
//
// Type: string
//

site_temp_spdb_url = "spdbp:://hail:0:/scr/eldora2/rsfdata/front/spdb/madis";

///////////// site_temp_station_name //////////////////
//
// Name of station for site temp data.
//
// If empty, we will use the closest data in time.
//
//
// Type: string
//

site_temp_station_name = "R797";

///////////// site_temp_data_type /////////////////////
//
// Data type instead of station name.
//
// If this is -1, site_temp_station_name is used. If not -1, this value 
//   is used instead of specifying the station name.
//
//
// Type: int
//

site_temp_data_type = 70778306;

///////////// site_temp_search_margin_secs ////////////
//
// Search margin when finding site temp data (secs).
//
// We search for the temperature closest in time to the radar volume. 
//   This is the search margin on either side of the sunscan time.
//
//
// Type: int
//

site_temp_search_margin_secs = 7200;

//======================================================================
//
// TEST PULSE ANALYSIS.
//
//======================================================================
 
///////////// compute_test_pulse_powers ///////////////
//
// Option to analyze the test pulse powers.
//
// If true, we will compute the test pulse for each channel, and write 
//   out results.
//
//
// Type: boolean
//

compute_test_pulse_powers = TRUE;

///////////// test_pulse_min_range_km /////////////////
//
// Range to start of test pulse (km).
//
// This delimits the test pulse gates in the moments.
//
//
// Type: double
//

test_pulse_min_range_km = 147.5;

///////////// test_pulse_max_range_km /////////////////
//
// Range to end of test pulse (km).
//
// This delimits the test pulse gates in the moments.
//
//
// Type: double
//

test_pulse_max_range_km = 147.8;

//======================================================================
//
// TRANSMITTER POWERS.
//
//======================================================================
 
///////////// compute_mean_transmit_powers ////////////
//
// Option to compute the mean xmit power for each channel.
//
// This depends on having the measured transmitter power in the time 
//   series.
//
//
// Type: boolean
//

compute_mean_transmit_powers = TRUE;

//======================================================================
//
// OUTPUT TEXT RESULTS.
//
//======================================================================
 
///////////// write_text_files ////////////////////////
//
// Option to write out text files.
//
// If false, the output fill be written to stdout.
//
//
// Type: boolean
//

write_text_files = TRUE;

///////////// text_output_dir /////////////////////////
//
// Dir for output text files.
//
// The results will be written to sub-directories named from the cal 
//   time.
//
//
// Type: string
//

text_output_dir = "$(DATA_DIR)/mascrad/qc/cal/spol/suncal/sband";

///////////// append_to_global_results_file ///////////
//
// Option to append results to global file.
//
//
// Type: boolean
//

append_to_global_results_file = TRUE;

///////////// global_file_name ////////////////////////
//
// Name for global output file.
//
//
// Type: string
//

global_file_name = "suncal.global.txt";

//======================================================================
//
// OUTPUT RESULTS TO MDV FILES.
//
//======================================================================
 
///////////// write_mdv_files /////////////////////////
//
// Option to write out grids to MDV files.
//
//
// Type: boolean
//

write_mdv_files = TRUE;

///////////// mdv_output_url //////////////////////////
//
// URL for output MDV files.
//
// For local writes, specify the directory. For remote writes, specify 
//   the full url: mdvp:://host::dir.
//
//
// Type: string
//

mdv_output_dir = "$(DATA_DIR)/mascrad/qc/mdv/spol/suncal/sband";

//======================================================================
//
// OUTPUT SUMMARY RESULTS TO SPDB XML.
//
//======================================================================
 
///////////// write_summary_to_spdb ///////////////////
//
// Option to write out summary results to SPDB.
//
// The summary will be in XML, stored in SPDB. It can then be retrieved 
//   for plotting or other purposes.
//
//
// Type: boolean
//

write_summary_to_spdb = TRUE;

///////////// spdb_output_url /////////////////////////
//
// URL for SPDB XML.
//
// For local writes, specify the directory. For remote writes, specify 
//   the full url: spdbp:://host::dir.
//
//
// Type: string
//

spdb_output_url = "spdbp:://hail:0:mascrad/qc/spdb/spol/suncal/sband/";

