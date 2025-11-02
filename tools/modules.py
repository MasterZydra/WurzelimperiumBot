#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# Project root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Dictionary of all code files with their imported modules
import_statements = {}

def main():
    # Read all python files in project root directory
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if os.path.isfile(file_path) and file.endswith('.py'):
            extract_imports(file_path)

    # Read all python files in the "src" directory
    for dirpath, _, files in os.walk(os.path.join(root_dir, 'src')):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(dirpath, file)
                extract_imports(file_path)

    # Generate a mermaid flowchart diagram to display the module dependencies
    mermaid_diagram = "# Modules\n\n```mermaid\nflowchart LR\n"
    for file, imports in import_statements.items():
        for imp in imports:
            if 'import ' in imp:
                module = imp.split(' ')[1].removesuffix(',')
                mermaid_diagram += f"    {file.replace('.', '_')}[{file}] --> {module.replace('.', '_')}[{module}]\n"
    mermaid_diagram += "```"
    # Write "/doc/Modules.md"
    with open(os.path.join(root_dir, 'doc', 'Modules.md'), 'w') as md_file:
        md_file.write(mermaid_diagram)

    print('Done')

def extract_imports(file_path):
    imports = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)

    module_name = os.path.relpath(file_path, root_dir)
    module_name = module_name.replace(os.sep, '.').removesuffix('.py')

    import_statements[module_name] = imports

if __name__ == "__main__":
    main()
