import random
from typing import Dict, List, Tuple

from mutation_generator import MutatedFile, MutatedFiles
from replacement import Mutation, Replacement, reverse


class Quiz:
    def __init__(
        self,
        files: MutatedFiles,
        reorder_prompt: str = "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
        find_mutation_prompt: str = "which line contains the mutation?",
        classify_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        fix_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        mc_opts: int = 4,
    ):
        # map of prompts used by ProblemSet init function
        prompts: Dict[str, str] = {
            "reorder": reorder_prompt,
            "find mutation": find_mutation_prompt,
            "classify mutation": classify_mutation_prompt,
            "fix mutation": fix_mutation_prompt,
        }

        # random other possible mutations to serve that serve to distract quizee
        # assuming 4 mc questions, we should have 3 distractors + the correct answer
        distractors: List[Mutation] = get_distractors(files, mc_opts)

        self.sets: List[ProblemSet] = []
        for list in files.mutated_files.values():
            for i, file in enumerate(list):
                self.sets.append(ProblemSet(file, i, prompts, distractors))


# creates 4 different distractors of random types
# one extra ditractor just in case one manages to be the correct answer
# if correct answer not in distractors, then 1 must get popped later
def get_distractors(files: MutatedFiles, mc_opts: int) -> List[Mutation]:
    mutation_distractors: List[Mutation] = []

    for _ in range(mc_opts):
        new_mut = random.choice(files.all_mutations)
        for mut in mutation_distractors:
            if new_mut.id == mut.id:
                break
        else:
            mutation_distractors.append(new_mut)

    return mutation_distractors


class ProblemSet:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompts: Dict[str, str],
        distractors: List[Mutation],
    ):
        self.id = file.mutation.id + str(mutation_num)
        self.reorder = Reorder(file, mutation_num, prompts["reorder"])
        self.findMutation = FindMutation(
            file, mutation_num, prompts["find mutation"], distractors
        )
        self.classifyMutation = ClassifyMutation(
            file, mutation_num, prompts["classifyMutation"], distractors
        )
        self.fixMutation = FixMutation(
            file, mutation_num, prompts["fix mutation"], distractors
        )


class Reorder:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
    ):
        self.problem_id = "reorder" + file.mutation.id.capitalize() + str(mutation_num)
        self.problem_type = "reorder"
        self.prompt = prompt
        self.answer = file.content


class FindMutation:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id = (
            "findMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type = "find mutation"
        self.prompt = prompt
        self.answer = file.content[file.mutation.line]

        self.distractors: List[str] = []
        for distractor in distractors:
            if distractor.line != file.mutation.line:
                self.distractors.append(file.content[distractor.line])

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class ClassifyMutation:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id = (
            "classifyMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type = "classify mutation"
        self.prompt = prompt
        self.answer = file.mutation.description

        self.distractors: List[str] = []
        for distractor in distractors:
            if distractor.description != file.mutation.description:
                self.distractors.append(distractor.description)

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class FixMutation:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id = (
            "fixMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type = "fix mutation"
        self.prompt = prompt
        self.answer = reverse(file.mutation.replacement)

        self.distractors: List[Replacement] = []
        for distractor in distractors:
            if distractor.replacement != file.mutation.replacement:
                self.distractors.append(reverse(distractor.replacement))

        if len(self.distractors) == len(distractors):
            self.distractors.pop()
