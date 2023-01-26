# Python template

Python template containing formatter, linter and other automatic verifications. First you need to install the Conda environment with required packages using `conda env create -f env.yml` (if you want to change the name of the environment from env to something else such as your_env_name, edit the entry "name" in the env.yml file). After successfully creating the environment, activate it using the `conda activate` command, such `conda activate your_env_name` (after this, all your commands will be executed into the python environment). Finally, execute the command 
`pre-commit install` to activate the pre-commit, so every time you make a commit it will verify your code and assure that you complied with all project standards.

## Using this template

When creating a new repository on GitHub, be sure to select in the template field `python_template` from LASSE organization. So, all the files in this template will be moved to your new project.

## VS Code integration

File `.vscode/settings.json` contains the default workspace configurations to automatically activate the formatter, linter, type check and sort imports in VS Code. Most of them promote file verification when saving the document. *Remember to select the correct python environment into the VS Code to enable it to use the packages installed into the environment*.

## GitHub Actions

Into `.github/` folder, there are specifications to GitHub actions to verify if the pushed commits are compliant with the project standards. You may need to activate GitHub actions in your repo to enable this verification.
