import os
import sys
import pathlib
import xml.etree.ElementTree as ET


def find_manifest(project_path):
    print(f"find all the manifest file in {project_path}")
    project_to_manifest = {}
    for full_path in pathlib.Path(project_path).rglob("AndroidManifest.xml"):
        folder = os.path.split(full_path)[0]
        if "build" in folder or folder == project_path:
            continue
        project_to_manifest[folder] = full_path
    return project_to_manifest


def find_gradle_files(project_path):
    print(f"find all the gradle file in {project_path}")
    project_to_gradle = {}
    for full_path in pathlib.Path(project_path).rglob("build.gradle"):
        folder = os.path.split(full_path)[0]
        if folder == project_path:
            continue
        project_to_gradle[folder] = full_path
    return project_to_gradle


def append_code_snippet(file_path, package_name):
    code_snippet = f"\nandroid {{\n    namespace \"{package_name}\"\n}}\n"

    try:
        # Read the contents of the file
        with open(file_path, 'r') as file:
            contents = file.readlines()

        # Find the position to insert the code snippet
        insert_position = 0
        for i, line in enumerate(contents):
            if line.strip().startswith("apply from:"):
                insert_position = i + 1

        # Insert the code snippet at the specified position
        contents.insert(insert_position, code_snippet)

        # Write the modified contents back to the file
        with open(file_path, 'w') as file:
            file.writelines(contents)
    except IOError:
        print("Error: File not found or unable to read/write.")


def remove_package_from_manifest(manifest_path, package_name):
    with open(manifest_path, 'r') as file:
        lines = file.readlines()

    with open(manifest_path, 'w') as file:
        for line in lines:
            if f'package="{package_name}"' in line:
                line = line.replace(f'package="{package_name}"', '')
                if line.strip() != "":
                    file.write(line)
            else:
                file.write(line)

    if not has_used_attributes(manifest_path):
        os.remove(manifest_path)


def has_used_attributes(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    attributes = set()

    # Collect all attributes used in the XML file
    for elem in root.iter():
        attributes.update(elem.attrib.keys())

    # Exclude common attributes like "xmlns" and "xmlns:android"
    common_attributes = {"xmlns", "xmlns:android"}
    attributes -= common_attributes

    return bool(attributes)  # Return True if any attributes are used, False otherwise


# Usage
def add_namespace(gradle_files, manifest_files):
    print("starting to move name space into gradle file")
    # loop manifest_files dictionary
    for project_path, manifest_path in manifest_files.items():
        with open(manifest_path) as f:
            try:
                package_name = extract_package_name(f.read())
            except ValueError as e:
                print(f"{e} for path {manifest_path}")
                continue
        key = project_path.split("/src/")[0]
        if key not in gradle_files:
            print(f"Gradle file not found for {key}")
            continue
        gradle_path = gradle_files[key]
        if check_namespace_exists(file_path=gradle_path, package_name=package_name):
            continue
        else:
            append_code_snippet(gradle_path, package_name)
            remove_package_from_manifest(manifest_path, package_name)


def check_namespace_exists(file_path, package_name):
    with open(file_path, 'r') as file:
        for line in file:
            if f'namespace = "{package_name}"' in line.strip():
                print(f"skipping {file_path} because it already has namespace")
                return True
    return False


def extract_package_name(xml_string):
    root = ET.fromstring(xml_string)
    if 'package' not in root.attrib:
        raise ValueError(f"Package name not found in AndroidManifest.xml path ")
    return root.attrib['package']


if __name__ == '__main__':
    project_path = input("Put your project path here: ")
    print("Current project path:", project_path)

    # project_path = "/Users/andreas.oentoro/StudioProjects/dax-android2/_geo"
    if project_path is None:
        print("Hey! I think you forgot to put the project path that you want to check")
        sys.exit(1)
    elif project_path == "help" or project_path == "-h":
        sys.exit(1)

    manifest_dict = find_manifest(project_path=project_path)
    gradle_dict = find_gradle_files(project_path=project_path)

    add_namespace(gradle_dict, manifest_dict)

    print("Process done! Please check if the manifest of the file replaced correctly")
