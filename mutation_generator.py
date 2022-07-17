import copy
import random
from typing import Dict, List

from file import File
from mutator import get_mutators
from replacement import Mutation


# contains:
# - contents of mutated file
# - info about mutation
class MutatedFile:
    def __init__(self, filename: str, content: List[str], mut: Mutation):
        self.filename = filename
        self.content = copy.deepcopy(content)
        self.content[mut.line] = mut.replacement.apply(self.content[mut.line])
        self.mutation = mut


# contains:
# - info on the inputted file
# - every possible mutation you can do on the file
# - a dictionary of mutated files indexed by mutator type
class MutatedFiles:
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
                mutated_files[mut.id].append(
                    MutatedFile(self.file.filename, self.file.content, mut)
                )

        else:
            randoms = random.sample(range(len(self.all_mutations)), 10)
            for i in randoms:
                mut = self.all_mutations[i]
                mutated_files[mut.id].append(
                    MutatedFile(self.file.filename, self.file.content, mut)
                )

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
