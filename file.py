import copy
import os
import random
from typing import Generator, List

from line import Line, LineGroup, group_lines
from mutation import Mutation
from mutator import get_mutators
from quiz_meta import QuizMeta


class ExtMeta:
    def __init__(self, filename: str):
        ext: str = filename.split(".")[-1]
        match ext:
            case "c":
                self.type = "c"
                self.html = "language-c"
                self.comment = " // "
            case "cc" | "cpp":
                self.type = "cpp"
                self.html = "language-cpp"
                self.comment = " // "
            case "hs":
                self.type = "haskell"
                self.html = "language-haskell"
                self.comment = " -- "
            case "js" | "ts":
                self.type = "javascript"
                self.html = "language-javascript"
                self.comment = " // "
            case "py":
                self.type = "python"
                self.html = "language-python"
                self.comment = " # "
            # if it's not recognizable we'll just assume it's c
            case _:
                self.html = "language-c"
                self.comment = " // "




# contains:
# - name of inputted file
# - every line of the file
# - trimmed content of the file (removing comments)
# - list of all possible mutations that can be performed on content
class File:
    def __init__(self, filename: str, meta: QuizMeta):
        self.filename: str = filename
        self.content: LineGroup
        self.mutations: List[Mutation] = []
        self.potential_distractors: List[Mutation] = []

        content: List[Line] = []

        if not os.path.exists(filename):
            print("ERROR: file not found")

        try:
            f = open(filename, "r")
            self.full_content = [x.rstrip() for x in f.read().splitlines()]

            for line in self.__get_lines():
                content.append(line)

            f.close()

        except FileNotFoundError:
            print(filename + " doesn't exist")

        self.content = group_lines(content)

        if meta.type == "mutation":
            for line_num, line in enumerate(content):
                for mutator_id, mutator in get_mutators().items():
                    for replacement in mutator.find_mutations(line.code):
                        self.mutations.append(
                            Mutation(
                                mutator_id=mutator_id,
                                description=mutator.description,
                                line_num=line_num,
                                line=line.code,
                                replacement=replacement,
                            )
                        )
            for mut in self.mutations:
                self.potential_distractors.append(mut)

            while len(self.mutations) > meta.max_mutations:
                self.mutations.pop(random.randrange(len(self.mutations)))

    # only retrieve lines contatining important stuff
    def __get_lines(self) -> Generator[Line, None, None]:
        # for tracking nested comments
        comment_type = ExtMeta(self.filename).comment
        nested_comments: int = 0
        prev_line: str = ""
        bracket_lines: List[str] = []
        comment: List[str] = []

        for i, line in enumerate(self.full_content):
            stripped = line.strip()

            # skip empty lines
            if stripped == "":
                i -= 1
                continue

            # skip line comments and preprocessor directives
            if (stripped.startswith(comment_type.strip())):
                comment.append(stripped)
                continue

            # recognize the beginning of a line comment
            if stripped.startswith("/*"):
                comment.append(stripped)
                nested_comments += 1
                if stripped.endswith("*/"):
                    nested_comments -= 1
                continue

            # skip "private" or "protected" declaration
            if stripped.startswith("private:") or stripped.startswith("protected:"):
                continue

            # recognize the end of a line comment
            if stripped.endswith("*/"):
                comment.append(stripped)
                nested_comments -= 1
                continue

            if stripped.endswith("{"):
                bracket_lines.append(stripped[:-1])

            if stripped == "{" and nested_comments == 0:
                bracket_lines.append(prev_line)
                temp = copy.deepcopy(comment)
                comment.clear()
                yield Line(line + comment_type + prev_line, temp)

            if stripped in ["}", "};", "});"] and nested_comments == 0:
                temp = copy.deepcopy(comment)
                comment.clear()
                yield Line(line + comment_type + bracket_lines.pop(), temp)
                continue

            # return line to mutate
            if nested_comments == 0:
                # print(stripped)
                temp = copy.deepcopy(comment)
                comment.clear()
                yield Line(line, temp)


# contains:
# - contents of mutated file
# - info about mutation
class MutatedFile:
    def __init__(self, filename: str, content: List[str], mut: Mutation):
        self.filename = filename
        self.content = copy.deepcopy(content)
        self.content[mut.num] = mut.after
        self.mutation = mut
