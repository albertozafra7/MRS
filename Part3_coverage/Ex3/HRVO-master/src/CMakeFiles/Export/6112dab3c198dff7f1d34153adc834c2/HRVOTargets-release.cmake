#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "HRVO::HRVO" for configuration "Release"
set_property(TARGET HRVO::HRVO APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HRVO::HRVO PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libHRVO.so.1.1.0"
  IMPORTED_SONAME_RELEASE "libHRVO.so.1"
  )

list(APPEND _cmake_import_check_targets HRVO::HRVO )
list(APPEND _cmake_import_check_files_for_HRVO::HRVO "${_IMPORT_PREFIX}/lib/libHRVO.so.1.1.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
