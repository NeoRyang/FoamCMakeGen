# Generate CMakeLists.txt from OpenFOAM Case

This script automates the process of creating a CMakeLists.txt file for a specific OpenFOAM case. It works by reading in the configuration data from the case’s Make/options and Make/files files and uses this data to write out a corresponding CMakeLists.txt.

## Usage

This script is intended to be used from the command line and does not require any command line arguments. From within the root directory of an OpenFOAM case, run the script:


python generate_cmake_lists.py [option]

Where option (optional) is Xcode or xcode. If this option is provided, the script will generate a project file named projectName.xcodeproj.

For more information about how to develop OpenFOAM with IDEs, you can refer to the following guide: [Develop OpenFOAM with IDEs](https://gitlab.com/seafloor-modeling-group/numericalmodeling/-/wikis/Develop-OpenFOAM-with-IDEs).


## How It Works

1. The script first reads in the case’s Make/options file and Make/files file.
2. It then parses these files to find the corresponding include directories and linked libraries for the case.
3. Using this information, it then generates a CMakeLists.txt file tailored to the case. This file includes instructions for the required minimum CMake version, the case’s name, the requirement of C++ standards, and configurations for OpenFOAM. It adds entries for the include directories and linked libraries that it found, and also handles dynamic links to libraries.
4. Lastly, the script creates a build directory in the current working directory, and runs CMake to generate build files in this directory.

The main benefit of this script is that it saves time and avoids manual errors in creating a CMakeLists.txt file for an OpenFOAM case. It’s especially useful for cases with a large number of include directories and linked libraries.
