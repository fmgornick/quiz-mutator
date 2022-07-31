import copy
import random
from pathlib import Path
from typing import Dict, List

from file import File, MutatedFile
from mutation import Mutation, random_mutator
from replacement import reverse


class Quiz:
    def __init__(
        self,
        file: File,
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
        distractors: List[Mutation] = get_distractors(file, mc_opts)

        self.sets: List[ProblemSet] = []
        for i, mutated_file in enumerate(file.mutated_files):
            self.sets.append(ProblemSet(mutated_file, i, prompts, distractors))


# creates 4 different distractors of random types
# one extra ditractor just in case one manages to be the correct answer
# if correct answer not in distractors, then 1 must get popped later
def get_distractors(file: File, mc_opts: int) -> List[Mutation]:
    mutation_distractors: List[Mutation] = []
    unused_lines = copy.deepcopy(file.content)

    for mut in sorted(file.mutations, key=lambda _: random.random()):
        if len(mutation_distractors) == mc_opts:
            break
        else:
            mutation_distractors.append(mut)

    while len(mutation_distractors) < mc_opts:
        mutation_distractors.append(random_mutator(unused_lines, mutation_distractors))

    return mutation_distractors


class ProblemSet:
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompts: Dict[str, str],
        distractors: List[Mutation],
    ):
        self.id = Path(file.filename).stem.capitalize() + str(mutation_num)
        self.content = file.content
        self.mutation = file.mutation

        self.reorder = Reorder(file, mutation_num, prompts["reorder"])
        self.findMutation = FindMutation(
            file, mutation_num, prompts["find mutation"], distractors
        )
        self.classifyMutation = ClassifyMutation(
            file, mutation_num, prompts["classify mutation"], distractors
        )
        self.fixMutation = FixMutation(
            file, mutation_num, prompts["fix mutation"], distractors
        )


class Question:
    problem_type = "generic"
    prompt = "generic question prompt"


class Reorder(Question):
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


class FindMutation(Question):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "findMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "find mutation"
        self.prompt: str = prompt
        self.answer: str = file.content[file.mutation.num]
        self.distractors: List[str] = []

        for distractor in distractors:
            if distractor.before != file.mutation.before:
                self.distractors.append(file.content[distractor.num])

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class ClassifyMutation(Question):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "classifyMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "classify mutation"
        self.prompt: str = prompt
        self.answer: str = file.mutation.description
        self.distractors: List[str] = []

        for distractor in distractors:
            if distractor.description != file.mutation.description:
                self.distractors.append(distractor.description)

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class FixMutation(Question):
    def __init__(
        self,
        file: MutatedFile,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "fixMutation" + file.mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "fix mutation"
        self.prompt: str = prompt
        self.answer: str = reverse(file.mutation.replacement).quiz_rep(
            file.mutation.after
        )

        self.distractors: List[str] = []
        for distractor in distractors:
            if distractor.replacement != file.mutation.replacement:
                self.distractors.append(
                    distractor.replacement.quiz_rep(distractor.before)
                )

        if len(self.distractors) == len(distractors):
            self.distractors.pop()
