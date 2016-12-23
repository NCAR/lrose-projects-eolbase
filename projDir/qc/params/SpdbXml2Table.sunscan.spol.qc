/**********************************************************************
 * TDRP params for SpdbXml2Table
 **********************************************************************/

//======================================================================
//
// SpdbXml2Table reads XML entries from an SPDB data base, and based on 
//   the specified parameters in the file, it reformats these into a text 
//   table.
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

//======================================================================
//
// DATA INPUT.
//
//======================================================================
 
///////////// input_url ///////////////////////////////
//
// URL to spdb data.
//
// This can either be (a) the path to the directory or (b) a url of the 
//   form 'spdbp:://hostname::dir'. For (a), if the path starts with '/' 
//   or '.', it will be treated as an absolute path. If not, it will be 
//   relative to DATA_DIR. For (b) the dir is relative to DATA_DIR on the 
//   host specified by hostname.
//
//
// Type: string
//

input_url = "spdbp:://hail:0:$(project)/qc/spdb/spol/suncal/sband/";

///////////// start_time //////////////////////////////
//
// The start time for extracting the data.
//
// Can be overridden by specifying -start on the command line.
//
//
// Type: struct
//   typedef struct {
//      int year;
//      int month;
//      int day;
//      int hour;
//      int min;
//      int sec;
//   }
//
//

start_time = {
    year = 2015,
    month = 5,
    day = 24,
    hour = 0,
    min = 0,
    sec = 0
};

///////////// end_time ////////////////////////////////
//
// The end time for extracting the data.
//
// Can be overridden by specifying -end on the command line.
//
//
// Type: struct
//   typedef struct {
//      int year;
//      int month;
//      int day;
//      int hour;
//      int min;
//      int sec;
//   }
//
//

end_time = {
    year = 2015,
    month = 7,
    day = 17,
    hour = 0,
    min = 0,
    sec = 0
};

///////////// data_type ///////////////////////////////
//
// Spdb data type, for constraining search.
//
// If non-zero, only entries with this data_type will be retrieved.
//
//
// Type: int
//

data_type = 0;

///////////// data_type_2 /////////////////////////////
//
// Spdb data type 2, for constraining search.
//
// If non-zero, only entries with this data_type_2 will be retrieved.
//
//
// Type: int
//

data_type_2 = 0;

//======================================================================
//
// Specify XML entries to be printed out.
//
//======================================================================
 
///////////// xml_entries /////////////////////////////
//
// Specify which XML entries to include in table.
//
// 	xml_tag_list: list of XML tags used to identify entry. These should 
//   be delimited in xml format, using < and >
// 	specify_label: do you want to use a label instead of the tags to 
//   comment the table?
// 	label: the label to use if specify_label is true
// .
//
//
// Type: struct
//   typedef struct {
//      string xml_tag_list;
//      boolean specify_label;
//      string label;
//      boolean required;
//   }
//
// 1D array - variable length.
//

xml_entries = {
  {
    xml_tag_list = "<RadarSunCal><CalTime>",
    specify_label = TRUE,
    label = "CalTime",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><radarName>",
    specify_label = TRUE,
    label = "radarName",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><radarSite>",
    specify_label = TRUE,
    label = "radarSite",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><radarLatitude>",
    specify_label = TRUE,
    label = "radarLatitude",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><radarLongitude>",
    specify_label = TRUE,
    label = "radarLongitude",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><radarAltitudeKm>",
    specify_label = TRUE,
    label = "radarAltitudeKm",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><VolumeNumber>",
    specify_label = TRUE,
    label = "VolumeNumber",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><meanSunEl>",
    specify_label = TRUE,
    label = "meanSunEl",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><meanSunAz>",
    specify_label = TRUE,
    label = "meanSunAz",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><nBeamsNoise>",
    specify_label = TRUE,
    label = "nBeamsNoise",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><noiseDbmHc>",
    specify_label = TRUE,
    label = "noiseDbmHc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><noiseDbmHx>",
    specify_label = TRUE,
    label = "noiseDbmHx",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><noiseDbmVc>",
    specify_label = TRUE,
    label = "noiseDbmVc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><noiseDbmVx>",
    specify_label = TRUE,
    label = "noiseDbmVx",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><maxPowerDbm>",
    specify_label = TRUE,
    label = "maxPowerDbm",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><quadPowerDbm>",
    specify_label = TRUE,
    label = "quadPowerDbm",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><maxPowerDbmHc>",
    specify_label = TRUE,
    label = "maxPowerDbmHc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><quadPowerDbmHc>",
    specify_label = TRUE,
    label = "quadPowerDbmHc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><maxPowerDbmVc>",
    specify_label = TRUE,
    label = "maxPowerDbmVc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><quadPowerDbmVc>",
    specify_label = TRUE,
    label = "quadPowerDbmVc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidAzOffset>",
    specify_label = TRUE,
    label = "centroidAzOffset",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidElOffset>",
    specify_label = TRUE,
    label = "centroidElOffset",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidAzOffsetHc>",
    specify_label = TRUE,
    label = "centroidAzOffsetHc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidElOffsetHc>",
    specify_label = TRUE,
    label = "centroidElOffsetHc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidAzOffsetVc>",
    specify_label = TRUE,
    label = "centroidAzOffsetVc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><centroidElOffsetVc>",
    specify_label = TRUE,
    label = "centroidElOffsetVc",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><nXpolPoints>",
    specify_label = TRUE,
    label = "nXpolPoints",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><meanXpolRatioDb>",
    specify_label = TRUE,
    label = "meanXpolRatioDb",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><S1S2>",
    specify_label = TRUE,
    label = "S1S2",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><zdrCorr>",
    specify_label = TRUE,
    label = "zdrCorr",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><meanXmitPowerHDbm>",
    specify_label = TRUE,
    label = "meanXmitPowerHDbm",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><meanXmitPowerVDbm>",
    specify_label = TRUE,
    label = "meanXmitPowerVDbm",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><xpolRatioDbFromSpdb>",
    specify_label = TRUE,
    label = "xpolRatioDb",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<RadarSunCal><siteTempFromSpdb>",
    specify_label = TRUE,
    label = "siteTemp",
    required = TRUE
  }
};

//======================================================================
//
// OUTPUT DETAILS.
//
//======================================================================
 
///////////// add_commented_header ////////////////////
//
// If true, write a commented header at the start of the output.
//
//
// Type: boolean
//

add_commented_header = TRUE;

///////////// comment_character ///////////////////////
//
// Character at start of comment lines.
//
// Each comment line will be start with this character.
//
//
// Type: string
//

comment_character = "#";

///////////// column_delimiter ////////////////////////
//
// Delimiter between columns.
//
//
// Type: string
//

column_delimiter = " ";

///////////// convert_boolean_to_integer //////////////
//
// If true, a 'false' value will be converted to 0, and a 'true' value 
//   to 1.
//
//
// Type: boolean
//

convert_boolean_to_integer = TRUE;

///////////// ignore_if_all_nans //////////////////////
//
// Do not print a line if all string values are 'nan'.
//
//
// Type: boolean
//

ignore_if_all_nans = TRUE;

///////////// replace_string_in_output ////////////////
//
// If true, change the specified string to the given replacement.
//
// This is done in the output, prior to the values being written to the 
//   table. It allows you to replace strings that might be problematic for 
//   processes that use the table for analysis.
//
//
// Type: boolean
//

replace_string_in_output = TRUE;

///////////// old_string //////////////////////////////
//
// String to be replaced in output table.
//
// See 'replace_string_in_output'.
//
//
// Type: string
//

old_string = " ";

///////////// new_string //////////////////////////////
//
// 'new_string' will replace 'old_string'.
//
// See 'replace_string_in_output'.
//
//
// Type: string
//

new_string = "_";

