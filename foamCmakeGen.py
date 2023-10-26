#!/usr/bin/env python
import re
import os
import shutil
import subprocess
import sys
from cmake_template import get_cmake_content


def read_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"[Error] The file {filename} was not found.")
        sys.exit(1)  # terminate the program

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

def create_folder_and_make(make_type:str=''):

    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    os.chdir('build')

    if make_type.lower() in ['x', 'xcode']:
        subprocess.call('cmake -GXcode ..', shell=True)
        subprocess.call('open .', shell=True)
    else:
        subprocess.call('cmake ..', shell=True)
        subprocess.call('make', shell=True)


projectPath = os.getcwd()
options_content = read_file(os.path.join(projectPath, 'Make/options'))
makefile_content = read_file(os.path.join(projectPath, 'Make/files'))

inc_path = get_string_between_terms(options_content, 'EXE_INC')
inc_path = inc_path.replace('(LIB_SRC)', '{OpenFOAM_SRC}')
inc_path = inc_path.replace('-I', '')

lib_path = get_string_between_terms(options_content, 'EXE_LIBS', "")

inc_path = get_valid_string(inc_path)
lib_path = get_valid_string(lib_path)
lib_path = lib_path.replace('-l','')

projectName = os.path.basename(projectPath)
src_name = makefile_content[0].strip()

print(f"Project name: {projectName}\n Project path: {projectPath}\n "\
    f"source name: {src_name}\n inc_path: {inc_path}\n Link dir: {lib_path}")
cmake_content =get_cmake_content(projectPath=projectPath,projectName=projectName,src_name=src_name,inc_path=inc_path,lib_path=lib_path)




with open("CMakeLists.txt", "w") as file:
    file.write(cmake_content)


if __name__ == "__main__":
    # Check if any argument is passed
    if len(sys.argv) > 1:
        create_folder_and_make(sys.argv[1])  # sys.argv[1] is the first command-line argument
    else:
        create_folder_and_make() 
