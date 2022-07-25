import copy
import random
from typing import Dict, List

from file import File
from mutation import Mutation


# contains:
# - contents of mutated file
# - info about mutation
class MutatedFile:
    def __init__(self, filename: str, content: List[str], mut: Mutation):
        self.filename = filename
        self.content = copy.deepcopy(content)
        self.content[mut.num] = mut.replacement.apply(self.content[mut.num])
        self.mutation = mut


# contains:
# - info on the inputted file
# - every possible mutation you can do on the file
# - a dictionary of mutated files indexed by mutator type
class MutatedFiles:
    def __init__(self, filename: str, max: int = 0):
        self.file = File(filename)

        self.mutations: List[Mutation] = []
        self.mutated_files: Dict[str, List[MutatedFile]] = {}
        self.__generate_mutated_files(max)

    # if max matters: randomly pick mutations and create mutated file objects from them
    # otherwise: create a mutated file object from every possible mutation
    def __generate_mutated_files(self, max: int) -> None:

        # tup[0] : int = line number mutation found on
        # tup[1] : str = type of mutation (mutator_id)
        # tup[2] : Replacement = change made on line
        if max == 0 or max >= len(self.mutations):
            for mut in self.mutations:
                if mut.id not in self.mutated_files:
                    self.mutated_files[mut.id] = []
                self.mutated_files[mut.id].append(
                    MutatedFile(self.file.filename, self.file.content, mut)
                )
                self.mutations.append(mut)

        else:
            randoms = random.sample(range(len(self.mutations)), 10)
            for i in randoms:
                mut = self.mutations[i]
                self.mutated_files[mut.id].append(
                    MutatedFile(self.file.filename, self.file.content, mut)
                )
                self.mutations.append(mut)
