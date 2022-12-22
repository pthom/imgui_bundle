import os


def external_libraries_dir():
    this_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    return this_dir


def repo_dir():
    r = os.path.abspath(external_libraries_dir() + "/..")
    return r
