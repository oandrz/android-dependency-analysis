import pathlib
import os
import sys

from graphviz import ExecutableNotFound, Source

os.environ["PATH"] += os.pathsep + '/usr/local/Cellar/graphviz/8.0.3/bin/'


def map_module_name_to_alias(module_name, project_path):
    mapped_module = ""
    for path in pathlib.Path(project_path).rglob("settings.gradle"):
        with open(path, encoding='utf-8') as f:
            for line in f:
                if module_name in line:
                    splited_line = line.strip().split(':')
                    mapped_module = splited_line[1].strip().replace('"', '')

    return mapped_module.replace("'", "")


def find_module(project_path):
    project_to_gradle_file = {}
    for full_path in pathlib.Path(project_path).rglob("build.gradle"):
        folder = os.path.split(full_path)[0]
        if folder == project_path:
            continue
        module_name = os.path.split(folder)[1]
        if "dax-map-navigation" in project_path:
            module_name = map_module_name_to_alias(module_name, project_path)
        project_to_gradle_file[module_name] = full_path
    return project_to_gradle_file


def extract_module_name_local_format(line):
    try:
        local_line_split = line.split("local.")
        if len(local_line_split) <= 1:
            return ""

        return local_line_split[1].replace("_", "-").replace(")", "").strip()
    except IndexError:
        print(f"There was an error when processing this path {line}")


def extract_module_name_normal_format(line):
    try:
        local_line_split = line.split(":")
        return local_line_split[1].replace("_", "-").replace("'", "").replace('"', "").replace(")", "").strip()
    except IndexError:
        print(f"There was an error when processing this path \n{line}")


def extract_module_name_from_line(file_line):
    if "local." in file_line:
        return extract_module_name_local_format(line=file_line)
    else:
        return extract_module_name_normal_format(line=file_line)


def find_dependencies_of_module(file_path, all_modules):
    module_dependencies = []

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            if "project" not in line:
                continue

            module_name_from_file = extract_module_name_from_line(line)
            for module in all_modules:
                if module_name_from_file == module:
                    module_dependencies.append(module.replace("-", "_"))
    return module_dependencies


def convert_to_dot(module_dependencies):
    result = ["digraph {"]
    for module, dependencies in module_dependencies.items():
        for dependency in dependencies:
            result.append(f"  {module} -> {dependency}")
    result.append("}")
    return "\n".join(result)


if __name__ == '__main__':
    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    # project_path = "/Users/andreas.oentoro/StudioProjects/dax-android2/_geo"
    if project_path is None:
        print("Hey! I think you forgot to put the project path that you want to check")
        sys.exit(1)
    elif project_path == "--help" or project_path == "-h":
        print("here's how to run the script ./dependency_analysis [project_path] --help|-h")
        sys.exit(1)

    print(f"checking project {project_path}")
    modules_result_raw = find_module(project_path=project_path)

    if len(modules_result_raw.items()) == 0:
        print("Dependencies not found, are you sure this is the right folder ?")
        sys.exit(1)

    module_dependencies_table = {}

    for module_name, gradle_file_path in modules_result_raw.items():
        dependencies = find_dependencies_of_module(file_path=gradle_file_path, all_modules=modules_result_raw.keys())
        module_dependencies_table[module_name.replace("-", "_")] = dependencies

    dot_language = convert_to_dot(module_dependencies_table)
    try:
        source = Source(dot_language)
        source.render(filename='dependencies', directory=f"{project_path}/output", format='jpg')
        print(f"Graph successfully generated at {project_path}/output")
    except ExecutableNotFound:
        print('Graphviz executable not found, please install by using brew install graphviz')
