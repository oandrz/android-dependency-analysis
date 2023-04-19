import pathlib
import os
import sys

from graphviz import ExecutableNotFound, Source

os.environ["PATH"] += os.pathsep + '/usr/local/Cellar/graphviz/8.0.3/bin/'


def find_module(project_path):
    project_to_gradle_file = {}
    for full_path in pathlib.Path(project_path).rglob("build.gradle"):
        folder = os.path.split(full_path)[0]
        if folder == project_path:
            continue
        module_name = os.path.split(folder)[1]
        project_to_gradle_file[module_name] = full_path
    return project_to_gradle_file


def extract_module_name_from_line(file_line):
    local_line_split = file_line.split("local.")
    if len(local_line_split) <= 1:
        return ""

    return local_line_split[1].replace("_", "-").replace(")", "").strip()


def find_dependencies_of_module(file_path, all_modules):
    module_dependencies = []

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            for module in all_modules:
                module_name_from_file = extract_module_name_from_line(line)
                if module_name_from_file == module and "project" in line:
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