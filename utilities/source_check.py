#!/usr/bin/env python3

# This file is part of SEAL-TK, and is distributed under the OSI-approved BSD
# 3-Clause License. See top-level LICENSE file or
# https://github.com/Kitware/seal-tk/blob/master/LICENSE for details.

import io
import os.path
import re
import subprocess
import sys


copyright_notice = \
r"""This file is part of SEAL-TK, and is distributed under the OSI-approved BSD
3-Clause License\. See top-level LICENSE file or
https://github\.com/Kitware/seal-tk/blob/master/LICENSE for details\."""

copyright_notice_cpp_re = "^/\* " + copyright_notice.replace("\n", "\n \* ") \
    + " \*/\n\n"
copyright_notice_cmake_re = "^# " + copyright_notice.replace("\n", "\n# ") \
    + "\n\n"
copyright_notice_py_re = "^(#!/usr/bin/env python3\n\n)?# " \
    + copyright_notice.replace("\n", "\n# ") + "\n\n"


def filename_components(s):
    head, tail = os.path.split(s)
    components = [tail]
    while head != "":
        head, tail = os.path.split(head)
        components.insert(0, tail)
    return components


def matches(s, pattern):
    return bool(re.search(pattern, s, flags=re.S))


class SourceFile:
    def __init__(self, source_directory, filename):
        self.source_directory = source_directory
        self.filename = filename
        self._contents = None

    def contents(self):
        if self._contents is None:
            with open(os.path.join(self.source_directory, self.filename),
                      "r") as f:
                self._contents = f.read()
        return self._contents

    def test(self):
        try:
            self.test_copyright()
            self.test_include_guards()
        except AssertionError as e:
            e.args = e.args + (self.filename,)
            raise e

    def test_copyright(self):
        if filename_components(self.filename)[0] == "src" and \
                matches(self.filename, r"\.(cpp|hpp|h\.in)$"):
            assert matches(self.contents(), copyright_notice_cpp_re)
        elif matches(self.filename, r"\.cmake$") or \
                filename_components(self.filename)[-1] == "CMakeLists.txt":
            assert matches(self.contents(), copyright_notice_cmake_re)
        elif matches(self.filename, r"\.py$"):
            assert matches(self.contents(), copyright_notice_py_re)

    def test_include_guards(self):
        if filename_components(self.filename)[0] == "src" and \
                matches(self.filename, r"\.(hpp|h\.in)$"):
            identifier = "_".join(filename_components(self.filename)[1:]) \
                .replace(".", "_")
            if matches(self.filename, r"\.h\.in$"):
                identifier = identifier[:-3]
            pattern = r"^([^\n]*\n){3}\n#ifndef SEALTK_" + identifier + \
                r"\n#define SEALTK_" + identifier + r"\n.*\n#endif\n$"
            assert matches(self.contents(), pattern)


def main():
    git = None
    doing = None
    for arg in sys.argv[1:]:
        if arg == "--git":
            doing = "git"
        elif doing == "git":
            git = arg
            doing = None

    finished = False
    source_directory = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    if git is not None:
        result = subprocess.run([git, "-C", source_directory, "ls-files"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        if not result.returncode:
            stdout = io.StringIO(result.stdout.decode())
            for filename in stdout:
                filename = filename.rstrip("\n")
                f = SourceFile(source_directory, filename)

                f.test()
            finished = True

    if not finished:
        for dirpath, dirnames, filenames in os.walk(source_directory):
            rel_dirpath = os.path.relpath(dirpath, source_directory)
            if filename_components(rel_dirpath)[0] != ".git":
                for filename in filenames:
                    f = SourceFile(source_directory,
                                   os.path.join(rel_dirpath, filename))

                    f.test()


if __name__ == "__main__":
    main()