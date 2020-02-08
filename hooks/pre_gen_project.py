"""Validates user input when using cookiecutter to start a project."""
import re


project = """{{ cookiecutter.project }}"""

if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", project):
    print("ERROR: project must be lower-case letters, numbers and dashes and must start with a letter")

    raise SystemExit(1)
