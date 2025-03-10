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

input_url = "spdbp:://hail:0:pecan/qc/spdb/spol/zdr_bias";

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
    year = 2011,
    month = 1,
    day = 1,
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
    year = 2011,
    month = 1,
    day = 1,
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
    xml_tag_list = "<ZdrBias><ZdrmInIceMean>",
    specify_label = TRUE,
    label = "ZdrmInIceMean",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc05.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc05.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc07.50>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc07.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc10.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc10.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc12.50>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc12.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc15.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc15.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc17.50>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc17.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc20.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc20.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc22.50>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc22.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc25.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc25.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc27.50>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc27.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrmInIcePerc30.00>",
    specify_label = TRUE,
    label = "ZdrmInIcePerc30.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIceMean>",
    specify_label = TRUE,
    label = "ZdrInIceMean",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc05.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc05.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc07.50>",
    specify_label = TRUE,
    label = "ZdrInIcePerc07.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc10.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc10.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc12.50>",
    specify_label = TRUE,
    label = "ZdrInIcePerc12.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc15.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc15.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc17.50>",
    specify_label = TRUE,
    label = "ZdrInIcePerc17.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc20.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc20.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc22.50>",
    specify_label = TRUE,
    label = "ZdrInIcePerc22.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc25.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc25.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc27.50>",
    specify_label = TRUE,
    label = "ZdrInIcePerc27.50",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><ZdrInIcePerc30.00>",
    specify_label = TRUE,
    label = "ZdrInIcePerc30.00",
    required = TRUE
  }
  ,
  {
    xml_tag_list = "<ZdrBias><TempSite>",
    specify_label = TRUE,
    label = "TempSite",
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

replace_string_in_output = FALSE;

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

