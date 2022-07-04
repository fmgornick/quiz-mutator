import os
import random
from typing import Dict, Generator, List

from mutator import get_mutators
from replacement import Mutation


# contains:
# - name of inputted file
# - every line of the file
# - trimmed content of the file (removing comments)
class File:
    def __init__(self, filename: str) -> None:
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


# contains:
# - contents of mutated file
# - info about mutation
class MutatedFile:
    def __init__(self, content: List[str], mut: Mutation) -> None:
        self.content = content
        self.content[mut.line] = mut.replacement.apply(self.content[mut.line])
        self.mutation = mut


# contains:
# - info on the inputted file
# - every possible mutation you can do on the file
# - a dictionary of mutated files indexed by mutator type
class Parser:
    def __init__(self, filename: str, max: int = 0):
        self.file = File(filename)
        self.all_mutations = self.__get_mutations()
        self.mutated_files = self.__generate_mutated_files(max)

    # if max matters: randomly pick mutations and create mutated file objects from them
    # otherwise: create a mutated file object from every possible mutation
    def __generate_mutated_files(self, max: int) -> Dict[str, List[MutatedFile]]:
        mutated_files: Dict[str, List[MutatedFile]] = {}

        # tup[0] : int = line number mutation found on
        # tup[1] : str = type of mutation (mutator_id)
        # tup[2] : Replacement = change made on line
        if max == 0 or max >= len(self.all_mutations):
            for mut in self.all_mutations:
                if mut.id not in mutated_files:
                    mutated_files[mut.id] = []
                mutated_files[mut.id].append(MutatedFile(self.file.content, mut))

        else:
            randoms = random.sample(range(len(self.all_mutations)), 10)
            for i in randoms:
                mut = self.all_mutations[i]
                mutated_files[mut.id].append(MutatedFile(self.file.content, mut))

        return mutated_files

    # create a list of every possible mutation that can be run on inputted file
    def __get_mutations(self) -> List[Mutation]:
        mutators = get_mutators()
        mutations: List[Mutation] = []

        for i, line in enumerate(self.file.content):
            for name, mutator in mutators.items():
                for replacement in mutator.find_mutations(line):
                    mutations.append(
                        Mutation(name, mutator.description, i, replacement)
                    )

        return mutations
