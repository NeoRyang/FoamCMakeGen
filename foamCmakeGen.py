import re
import os
import shutil
import subprocess

def read_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()

def get_string_between_terms(contents, start_term, end_term=""):
    term_lines = [line for line in contents if line.strip().startswith(start_term)]
    term_string = ""
    if term_lines:
        start_index = contents.index(term_lines[0])
        term_lines = []
        for line in contents[start_index + 1:]:
            if line.strip() == end_term:
                break
            term_lines.append(line.strip())
        term_string = ' '.join(term_lines)
    return term_string

def get_valid_string(term_string):
    term_string = re.sub('\*', '', term_string)
    term_string = term_string.replace('\\', '')
    term_string = ' '.join(term_string.split())
    return term_string

def create_folder_and_make(project_path):
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    os.chdir('build')
    subprocess.call('cmake ..', shell=True)
    subprocess.call('make', shell=True)


projectPath = os.getcwd()
options_content = read_file(os.path.join(projectPath, 'Make/options'))
makefile_content = read_file(os.path.join(projectPath, 'Make/files'))

include_dir = get_string_between_terms(options_content, 'EXE_INC')
linkLibs = get_string_between_terms(options_content, 'EXE_LIBS', "")
include_dir = get_valid_string(include_dir)
linkLibs = get_valid_string(linkLibs)

projectName = os.path.basename(projectPath)
source_name = makefile_content[0].strip()

print(f"Project name: {projectName}\n Project path: {projectPath}\n "\
    f"source name: {source_name}\n include_dir: {include_dir}\n Link dir: {linkLibs}")

# creating the CMakeLists.txt file should be handled in a separate function

cmake_content = f"""
cmake_minimum_required(VERSION 3.20 FATAL_ERROR)
# Check valid OpenFOAM
if(DEFINED ENV{{WM_PROJECT_DIR}})
        MESSAGE(STATUS "OpenFOAM: " $ENV{{WM_PROJECT_DIR}})
else()
        message(FATAL_ERROR "The OpenFOAM bashrc is not sourced")
endif(DEFINED ENV{{WM_PROJECT_DIR}})
list(APPEND CMAKE_MODULE_PATH "$ENV{{WM_PROJECT_DIR}}/cmake")
list(APPEND CMAKE_MODULE_PATH "${{CMAKE_CURRENT_SOURCE_DIR}}/cmake")
set(CMAKE_XCODE_GENERATE_SCHEME TRUE)  #需要再最前面设置这个CMAKE_XCODE_GENERATE_SCHEME变量为TRUE才能使xcode项目的scheme设置生效

project({projectName} LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# =====================================================================================
#             OpenFOAM configurations: elegant way!
# -------------------------------------------------------------------------------------
include(OpenFOAM)
# =====================================================================================
#             Include path configuration, similar to that in Make/options
include_directories({include_dir})
# =====================================================================================
set(PATH_SRC "src_Foundation")
if(${{OpenFOAM_VERSION}} MATCHES "v([0-9]*)")
    set(PATH_SRC "{projectPath}")
endif()
#add_subdirectory(${{PATH_SRC}})
include_directories(${{PATH_SRC}})

add_executable(${{PROJECT_NAME}} ${{PATH_SRC}}/{source_name})

# dynamic link
#target_link_libraries(${{PROJECT_NAME}} OpenFOAM dl m Pstream finiteVolume fvOptions meshTools)
target_link_libraries(${{PROJECT_NAME}} OpenFOAM dl Pstream {linkLibs})

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
with open("CMakeLists.txt", "w") as file:
    file.write(cmake_content)
create_folder_and_make(projectPath)

