import copy
from typing import Dict, List, Tuple

from mutation_generator import MutatedFile, MutatedFiles
from mutator import get_mutators
from replacement import Mutation, Replacement

mutation_descriptions: Dict[str, str] = {}
for name, mutator in get_mutators().items():
    mutation_descriptions[name] = mutator.description


class Quiz:
    def __init__(
        self,
        files: MutatedFiles,
        reorder_prompt: str = "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
        find_mutation_prompt: str = "which line contains the mutation?",
        classify_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        fix_mutation_prompt: str = "what change needs to be made for the function to work properly?",
    ):
        self.sections: List[Tuple[Problem, Problem, Problem, Problem]] = []
        for list in files.mutated_files.values():
            for i, file in enumerate(list):
                tup = (
                    Reorder(file, i, reorder_prompt),
                    FindMutation(file, i, find_mutation_prompt),
                    ClassifyMutation(file, i, classify_mutation_prompt),
                    FixMutation(file, i, find_mutation_prompt),
                )
                self.sections.append(tup)


class Problem:
    problem_id = "genericProblem"
    prompt = "generic problem prompt"


class Reorder(Problem):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str = "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
    ):
        self.problem_id = "reorder" + file.mutation.id.capitalize() + str(mutation_num)
        self.prompt = prompt
        self.answer = file.content


class FindMutation(Problem):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str = "which line contains the mutation?",
    ):
        self.problem_id = (
            "findMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.prompt = prompt

        mut_line = file.mutation.line
        self.answer = file.content[mut_line]

        self.distractors: List[str] = []
        for i, line in enumerate(file.content):
            if i != mut_line:
                self.distractors.append(line)


class ClassifyMutation(Problem):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        mutation_type: str,
        prompt: str = "what change needs to be made for the function to work properly?",
    ):
        self.problem_id = (
            "classifyMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.prompt = prompt
        self.answer = file.mutation.description

        self.distractors = copy.deepcopy(mutation_descriptions)
        del self.distractors[file.mutation.id]


class FixMutation(Problem):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str = "what change needs to be made for the function to work properly?",
    ):
        self.problem_id = (
            "fixMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.prompt = prompt

        mut = file.mutation
        rep = mut.replacement
        rev_rep = Replacement(rep.start_col, rep.end_col, rep.new_val, rep.old_val)

        self.answer = Mutation(mut.id, mut.description, mut.line, rev_rep)
