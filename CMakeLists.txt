cmake_minimum_required(VERSION 3.24)
project(TTPlayerRes LANGUAGES C RC)
if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Configure with a Visual Studio generator and -A Win32")
endif()
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(TTPRES_BUILD_VERSION "" CACHE STRING "Beijing date version: yyyy.MM.dd[pN]")
if(NOT TTPRES_BUILD_VERSION)
  execute_process(COMMAND "${Python3_EXECUTABLE}" -c
    "import datetime; print(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d'))"
    OUTPUT_VARIABLE TTPRES_BUILD_VERSION OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
endif()
set(generated "${CMAKE_CURRENT_BINARY_DIR}/generated")
file(GLOB_RECURSE resource_sources CONFIGURE_DEPENDS "resources/*" "tools/*.py" "sdk/*")
add_custom_command(OUTPUT "${generated}/original.res" "${generated}/metadata.rc" "${generated}/abi.bin" "${generated}/build.json"
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_resources.py"
    --source "${CMAKE_CURRENT_SOURCE_DIR}" --output "${generated}" --version "${TTPRES_BUILD_VERSION}"
  DEPENDS ${resource_sources} VERBATIM)
# No dummy C/C++ object: no CRT, DllMain, static initializers or thunks.
add_library(ttpres SHARED "${generated}/original.res" "${generated}/metadata.rc" resources/extended/player.rc)
set_source_files_properties("${generated}/original.res" PROPERTIES EXTERNAL_OBJECT TRUE GENERATED TRUE)
set_target_properties(ttpres PROPERTIES LINKER_LANGUAGE C PREFIX "" OUTPUT_NAME "ttpres")
target_include_directories(ttpres PRIVATE "${generated}" "${CMAKE_CURRENT_SOURCE_DIR}/sdk/include")
target_link_options(ttpres PRIVATE /NOENTRY /NODEFAULTLIB /MACHINE:X86 /BASE:0x6FF50000 /SUBSYSTEM:WINDOWS,5.01 /INCREMENTAL:NO /MANIFEST:NO /Brepro)
add_custom_command(TARGET ttpres POST_BUILD
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/finalize.py" "$<TARGET_FILE:ttpres>"
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/audit.py"
    --dll "$<TARGET_FILE:ttpres>" --manifest "${CMAKE_CURRENT_SOURCE_DIR}/resources/original/manifest.json"
    --output "$<TARGET_FILE_DIR:ttpres>/ttpres-component.json" VERBATIM)
install(FILES "$<TARGET_FILE:ttpres>" DESTINATION . COMPONENT Runtime)
