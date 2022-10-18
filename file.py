import copy
import os
import random
from typing import Generator, List

from mutation import Mutation
from mutator import get_mutators
from quiz_meta import QuizMeta


class Line:
    def __init__(self, line: str, comment: List[str]):
        self.line = line
        self.comment = comment


# contains:
# - name of inputted file
# - every line of the file
# - trimmed content of the file (removing comments)
# - list of all possible mutations that can be performed on content
class File:
    def __init__(self, filename: str, meta: QuizMeta):
        self.filename: str = filename
        self.content: List[Line] = []
        self.mutations: List[Mutation] = []

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

        if meta.type == "mutation":
            for line_num, line in enumerate(self.content):
                for mutator_id, mutator in get_mutators().items():
                    for replacement in mutator.find_mutations(line.line):
                        self.mutations.append(
                            Mutation(
                                mutator_id=mutator_id,
                                description=mutator.description,
                                line_num=line_num,
                                line=line.line,
                                replacement=replacement,
                            )
                        )

            while len(self.mutations) > meta.max_mutations:
                self.mutations.pop(random.randrange(len(self.mutations)))

    # only retrieve lines contatining important stuff
    def __get_lines(self) -> Generator[Line, None, None]:
        in_comment = False
        comment: List[str] = []

        for i, line in enumerate(self.full_content):
            stripped = line.strip()

            # skip empty lines
            if stripped == "":
                i -= 1
                continue

            # skip line comments and preprocessor directives
            if (
                stripped.startswith("//")
                or stripped.startswith("#")
                or stripped.startswith("--")
            ):
                comment.append(stripped)
                continue

            # skip empty lines or "bracket onlys"
            if stripped in ["", "{", "}", "};", "});", ")"]:
                continue

            # recognize the beginning of a line comment
            if stripped.startswith("/*"):
                comment.append(stripped)
                in_comment = True
                if stripped.endswith("*/"):
                    in_comment = False
                continue

            # skip "private" or "protected" declaration
            if stripped.startswith("private:") or stripped.startswith("protected:"):
                continue

            # recognize the end of a line comment
            if stripped.endswith("*/"):
                comment.append(stripped)
                in_comment = False
                continue

            # remove opening braces
            if stripped.endswith("{"):
                stripped = stripped[:-1]

            # return line to mutate
            if not in_comment:
                # print(stripped)
                comment.clear()
                yield Line(line, comment)


# contains:
# - contents of mutated file
# - info about mutation
class MutatedFile:
    def __init__(self, filename: str, content: List[str], mut: Mutation):
        self.filename = filename
        self.content = copy.deepcopy(content)
        self.content[mut.num] = mut.after
        self.mutation = mut
