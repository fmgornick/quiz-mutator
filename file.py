import os
from typing import Generator, List


class File:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.content: List[str] = []

        if not os.path.exists(filename):
            print("ERROR: file not found")

        try:
            f = open(filename, "r")
            lines: List[str] = []

            for line in f.read().splitlines():
                if line != "":
                    lines.append(line)

            for line in self.__get_lines(lines):
                self.content.append(line)

            f.close()

        except FileNotFoundError:
            print(filename + " doesn't exist")

    def __get_lines(self, lines) -> Generator[str, None, None]:
        in_comment = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # skip empty lines
            if stripped == "":
                i -= 1
                continue

            # skip line comments and preprocessor directives
            if stripped.startswith("//") or stripped.startswith("#"):
                continue

            # recognize the beginning of a line comment
            if stripped.startswith("/*"):
                in_comment = True
                if stripped.endswith("*/"):
                    in_comment = False
                continue

            # skip "private" or "protected" declaration
            if stripped.startswith("private:") or stripped.startswith("protected:"):
                continue

            # recognize the end of a line comment
            if stripped.endswith("*/"):
                in_comment = False
                continue

            print(line)
            # return line to mutate
            if not in_comment:
                yield line.lstrip()
