def get_cmake_content(projectPath,projectName,src_name,inc_path,lib_path):

    cmake_content = f"""
cmake_minimum_required(VERSION 3.20 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "${{CMAKE_CURRENT_SOURCE_DIR}}/cmake")
set(CMAKE_XCODE_GENERATE_SCHEME TRUE)  #需要再最前面设置这个CMAKE_XCODE_GENERATE_SCHEME变量为TRUE才能使xcode项目的scheme设置生效

project({projectName} LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# =====================================================================================
#             OpenFOAM configurations: elegant way!
# -------------------------------------------------------------------------------------

# Basic configuration of OpenFOAM in cmake

# Check valid OpenFOAM
if(DEFINED ENV{{WM_PROJECT_DIR}})
	MESSAGE(STATUS "OpenFOAM: " $ENV{{WM_PROJECT_DIR}})
else()
	message(FATAL_ERROR "The OpenFOAM bashrc is not sourced")
endif(DEFINED ENV{{WM_PROJECT_DIR}})
set(OpenFOAM_VERSION $ENV{{WM_PROJECT_VERSION}}) 
set(OpenFOAM_DIR $ENV{{WM_PROJECT_DIR}})
set(OpenFOAM_LIB_DIR $ENV{{FOAM_LIBBIN}})
set(OpenFOAM_SRC $ENV{{FOAM_SRC}})
set(OpenFOAM_USER_APPBIN $ENV{{FOAM_USER_APPBIN}})

# ====================== Some difference between ESI version and Foundation version ==================
# Of course you can change some parameters here, e.g., some pre-settings in ~/.OpenFOAM/prefs.h
set(PATH_LIB_OPENMPI "openmpi-system")  # Foundation version
set(DEFINITIONS_COMPILE "-std=c++11 -DWM_ARCH_OPTION=64 -DWM_DP -DWM_LABEL_SIZE=32 -Wall -Wextra -Wno-unused-parameter -Wno-overloaded-virtual -Wno-unused-variable -Wno-unused-local-typedef -Wno-invalid-offsetof -Wno-deprecated-register -Wno-undefined-var-template -O0 -g -DFULLDEBUG -DNoRepository -ftemplate-depth-100 -fPIC")

if(${{OpenFOAM_VERSION}} MATCHES "v([0-9]*)")       # ESI
    set(PATH_LIB_OPENMPI "sys-openmpi")
    set(DEFINITIONS_COMPILE "-std=c++14 -m64 -pthread -ftrapping-math -DOPENFOAM=2106 -DWM_DP -DWM_LABEL_SIZE=32 -Wall -Wextra -Wold-style-cast -Wnon-virtual-dtor -Wno-unused-parameter -Wno-invalid-offsetof -Wno-undefined-var-template -Wno-unknown-warning-option  -O3  -DNoRepository -ftemplate-depth-100 -fPIC -DIMPLEMENT_ACTIVATION -Wl,-execute,-undefined,dynamic_lookup")
endif()
# =====================================================================================================
# Compiling configure
add_definitions("${{DEFINITIONS_COMPILE}}")
# ======== OS specific setting =============
if(APPLE)
    add_definitions(" -Ddarwin64 ")
else()
    add_definitions("-Dlinux64")
endif(APPLE)

# ==========================================

include_directories(. 
                    ${{OpenFOAM_SRC}}/OpenFOAM/lnInclude  
                    ${{OpenFOAM_SRC}}/OSspecific/POSIX/lnInclude 
                    ${{OpenFOAM_SRC}}/finiteVolume/lnInclude 
                    )

link_directories(${{OpenFOAM_LIB_DIR}} ${{OpenFOAM_LIB_DIR}}/dummy ${{OpenFOAM_LIB_DIR}}/${{PATH_LIB_OPENMPI}})
# =====================================================================================
#             Include path configuration, similar to that in Make/options
# include_directories(${{OpenFOAM_SRC}}/meshTools/lnInclude)
include_directories({inc_path})

# =====================================================================================
set(PATH_SRC "src_Foundation")
if(${{OpenFOAM_VERSION}} MATCHES "v([0-9]*)") 
    set(PATH_SRC {projectPath})
endif()
#add_subdirectory(${{PATH_SRC}})
include_directories(${{PATH_SRC}})

add_executable(${{PROJECT_NAME}} ${{PATH_SRC}}/{src_name})
set_target_properties(${{PROJECT_NAME}}  PROPERTIES 
    RUNTIME_OUTPUT_DIRECTORY ${{OpenFOAM_USER_APPBIN}})
# dynamic link
target_link_libraries(${{PROJECT_NAME}} OpenFOAM dl m Pstream {lib_path})

# =====================================================================================
#             XCode scheme configurations
# -------------------------------------------------------------------------------------
if (CMAKE_GENERATOR MATCHES "Xcode")
    message(STATUS "Set xcode scheme-run-arguments")
    # 设置xcode运行时的环境变量，因为OpenFOAM.dylib会检查OpenFOAM环境变量是否有效，否则直接退出无法运行
    # 需要在CMakeLists.txt的最前面设置 CMAKE_XCODE_GENERATE_SCHEME 为TRUE使其生效
    # set(CMAKE_XCODE_GENERATE_SCHEME TRUE)
    set_property (TARGET ${{PROJECT_NAME}} PROPERTY XCODE_SCHEME_ARGUMENTS "-case ${{CMAKE_SOURCE_DIR}}/testCase")
    set_property(TARGET ${{PROJECT_NAME}} PROPERTY XCODE_SCHEME_ENVIRONMENT WM_PROJECT_DIR=$ENV{{WM_PROJECT_DIR}} WM_PROJECT=$ENV{{WM_PROJECT}} WM_PROJECT_VERSION=$ENV{{WM_PROJECT_VERSION}})
endif ()
# =====================================================================================
# ======================= Message out ===========================
message(STATUS "Configuration type: " ${{CMAKE_CONFIGURATION_TYPES}})
"""
    return cmake_content