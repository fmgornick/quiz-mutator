import random
from typing import Dict, List, Tuple

from file import File
from mutated_file import MutatedFile
from mutator import get_mutators
from replacement import Replacement


class Meta:
    def __init__(self, filename: str, max: int = 0):
        self.file = File(filename)
        self.all_mutations = self.__get_mutations()
        self.mutated_files = self.__generate_mutated_files(max)

    def __generate_mutated_files(self, max: int) -> Dict[str, List[MutatedFile]]:
        mutated_files: Dict[str, List[MutatedFile]] = {}

        # tup[0] : int = line number mutation found on
        # tup[1] : str = type of mutation (mutator_id)
        # tup[2] : Replacement = change made on line
        if max == 0 or max >= len(self.all_mutations):
            for tup in self.all_mutations:
                mutated_files[tup[1]].append(
                    MutatedFile(self.file, tup[2], tup[1], tup[0])
                )

        else:
            randoms = random.sample(range(len(self.all_mutations)), 10)
            for i in randoms:
                tup = self.all_mutations[i]
                mutated_files[tup[1]].append(
                    MutatedFile(self.file, tup[2], tup[1], tup[0])
                )

        return mutated_files

    def __get_mutations(self) -> List[Tuple[int, str, Replacement]]:
        mutators = get_mutators()
        mutations: List[Tuple[int, str, Replacement]] = []

        for i, line in enumerate(self.file.content):
            for name, mutator in mutators.items():
                for mutation in mutator.find_mutations(line):
                    mutations.append((i, name, mutation))

        return mutations
