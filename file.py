import os
from typing import Generator, List


# contains:
# - name of inputted file
# - every line of the file
# - trimmed content of the file (removing comments)
class File:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.content: List[str] = []

        if not os.path.exists(filename):
            print("ERROR: file not found")

        try:
            f = open(filename, "r")
            self.full_content = [x.rstrip() for x in f.read().splitlines()]

            for line in self.__get_lines():
                self.content.append(line)

            f.close()

        except FileNotFoundError:
            print(filename + " doesn't exist")

    # only retrieve lines contatining importent stuff
    def __get_lines(self) -> Generator[str, None, None]:
        in_comment = False

        for i, line in enumerate(self.full_content):
            stripped = line.strip()

            # skip empty lines
            if stripped == "":
                i -= 1
                continue

            # skip line comments and preprocessor directives
            if stripped.startswith("//") or stripped.startswith("#"):
                continue

            # skip empty lines or "bracket onlys"
            if stripped in ["", "{", "}", "};", "});", ")"]:
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

            # remove opening braces
            if stripped.endswith("{"):
                stripped = stripped[:-1]

            # return line to mutate
            if not in_comment:
                print(stripped)
                yield stripped
