import copy
import random
from pathlib import Path
from typing import Dict, List

from file import File
from mutation import Mutation, random_mutation
from quiz_meta import QuizMeta
from replacement import reverse


class Quiz:
    def __init__(self, file: File, meta: QuizMeta):
        self.type = meta.type
        # map of prompts used by ProblemSet init function
        match self.type:
            case "parsons":
                self.question = Parson(file, meta.reorder_prompt)
            case "mutation":
                prompts: Dict[str, str] = {
                    "reorder": meta.reorder_prompt,
                    "find mutation": meta.find_mutation_prompt,
                    "classify mutation": meta.classify_mutation_prompt,
                    "fix mutation": meta.fix_mutation_prompt,
                }

                # random other possible mutations to serve that serve to distract quizee
                # assuming 4 mc questions, we should have 3 distractors + the correct answer
                distractors: List[Mutation] = get_distractors(file, meta.mc_distractors + 1)

                self.sets: List[ProblemSet] = []
                for i, mutation in enumerate(file.mutations):
                    self.sets.append(ProblemSet(file, mutation, i, prompts, distractors))


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

    # add multiple choice distractors to our problem
    # make sure no two distractors are the same
    while len(mutation_distractors) < mc_opts:
        d = random_mutation(unused_lines, mutation_distractors)
        for mut in mutation_distractors:
            if d.after != mut.after:
                mutation_distractors.append(d)

    return mutation_distractors


class ProblemSet:
    def __init__(
        self,
        file: File,
        mutation: Mutation,
        mutation_num: int,
        prompts: Dict[str, str],
        distractors: List[Mutation],
    ):
        self.id = Path(file.filename).stem.capitalize() + str(mutation_num)
        self.filetype = file.filetype
        self.mutation = mutation
        self.content = file.content
        self.content[mutation.num].code = mutation.after

        # self.order = Reorder(self.content, mutation, mutation_num, prompts["reorder"])
        self.findMutation = FindMutation(file, mutation, mutation_num, prompts["find mutation"], distractors)
        self.classifyMutation = ClassifyMutation(mutation, mutation_num, prompts["classify mutation"], distractors)
        self.fixMutation = FixMutation(mutation, mutation_num, prompts["fix mutation"], distractors)


class Question:
    problem_type = "generic"
    prompt = "generic question prompt"


class Parson(Question):
    def __init__( self, file: File, prompt: str):
        self.id = Path(file.filename).stem.capitalize()
        self.problem_type = "parsons"
        self.prompt = prompt
        self.answer = file.content

class Reorder(Question):
    def __init__(
        self,
        content: List[str],
        mutation: Mutation,
        mutation_num: int,
        prompt: str,
    ):
        self.problem_id = "reorder" + mutation.id.capitalize() + str(mutation_num)
        self.problem_type = "reorder"
        self.prompt = prompt
        self.answer = content


class FindMutation(Question):
    def __init__(
        self,
        file: File,
        mutation: Mutation,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "findMutation" + mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "find mutation"
        self.prompt: str = prompt
        self.answer: str = file.content[mutation.num].code
        self.distractors: List[str] = []

        for distractor in distractors:
            if distractor.before != mutation.before:
                self.distractors.append(file.content[distractor.num].code)

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class ClassifyMutation(Question):
    def __init__(
        self,
        mutation: Mutation,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "classifyMutation" + mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "classify mutation"
        self.prompt: str = prompt
        self.answer: str = mutation.description
        self.distractors: List[str] = []

        for distractor in distractors:
            if distractor.description != mutation.description:
                self.distractors.append(distractor.description)

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


class FixMutation(Question):
    def __init__(
        self,
        mutation: Mutation,
        mutation_num: int,
        prompt: str,
        distractors: List[Mutation],
    ):
        self.problem_id: str = (
            "fixMutation" + mutation.id.capitalize() + str(mutation_num)
        )
        self.problem_type: str = "fix mutation"
        self.prompt: str = prompt
        self.answer: str = reverse(mutation.replacement).quiz_rep(mutation.after)

        self.distractors: List[str] = []
        for distractor in distractors:
            if distractor.replacement != mutation.replacement:
                self.distractors.append(
                    distractor.replacement.quiz_rep(distractor.before)
                )

        if len(self.distractors) == len(distractors):
            self.distractors.pop()
