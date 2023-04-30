# Gradle Dependency Analysis Script

## What is it
Generate  module dependency of a module or project. Run the command and it will generate image like this.

[Image]

## How to use

### Pre-requisite
- `Python version >= 3.7`


### How to run the script ?
```bash
python dependency_analysis.py [project_path] --help|-h
```

### Other Alternative:
- Download this zip from [here](https://drive.google.com/drive/folders/1eA_qoN1kpoSxS72j0ajKJt0dF84xYKmq?usp=share_link)
- Parse all the item and move to the directory that you wanted
- Open your terminal
- From your terminal go into the path where you extract the data.
- run the script by using `./dependency_analysis [project_path] --help |h`

## Limitation
- Only able to create dependency between module.
- The dependency that are generated are only the local dependency or module in the project.

## Plan

[x] Create Dependency Generator Image

[] Integrate with dependency analysis