import copy
import random
from pathlib import Path
from typing import Dict, List

from file import File
from mutation import Mutation
from quiz_meta import QuizMeta
from replacement import reverse_rep


# Quiz object created from metadata
class Quiz:
    def __init__(self, file: File, meta: QuizMeta):
        self.type = meta.type
        # map of prompts used by ProblemSet init function
        match self.type:
            case "parsons":
                self.question = Parson(file, meta.reorder_prompt)
            case "mutation":
                prompts: Dict[str, str] = {
                    "find mutation": meta.find_mutation_prompt,
                    "classify mutation": meta.classify_mutation_prompt,
                    "fix mutation": meta.fix_mutation_prompt,
                }

                self.sets: List[ProblemSet] = []
                for i, mutation in enumerate(file.mutations):
                    self.sets.append(ProblemSet(file, mutation, i, prompts, meta.mc_distractors))


# creates 4 different distractors of random types
# one extra ditractor just in case one manages to be the correct answer
# if correct answer not in distractors, then 1 must get popped later
def get_distractors(mutation: Mutation, others: List[Mutation], num_distractors: int) -> List[Mutation]:
    mutation_distractors: List[Mutation] = []
    ids: List[str] = []

    # add multiple choice distractors to our problem
    # make sure no two distractors are the same
    while len(mutation_distractors) < num_distractors + 1:
        d = random.choice(list(others))
        if d != mutation:
            if d.id not in ids:
                mutation_distractors.append(d)
                ids.append(d.id)

    return mutation_distractors


# for mutation questions, we have a set of 3 questions for each mutation
class ProblemSet:
    def __init__(
        self,
        file: File,
        mutation: Mutation,
        mutation_num: int,
        prompts: Dict[str, str],
        num_distractors: int,
    ):
        self.id = Path(file.filename).stem.capitalize() + str(mutation_num)
        self.mutation = mutation
        self.content = copy.deepcopy(file.content)
        self.content[mutation.num].code = mutation.after
        self.distractors = get_distractors(mutation, file.potential_distractors, num_distractors)

        self.findMutation = FindMutation(file, mutation, mutation_num, prompts["find mutation"], self.distractors)
        self.classifyMutation = ClassifyMutation(mutation, mutation_num, prompts["classify mutation"], self.distractors)
        self.fixMutation = FixMutation(mutation, mutation_num, prompts["fix mutation"], self.distractors)


# Question parent class (4 child classes: Parson, FindMutation, FixMutation, ClassifyMutation)
# each question has an ID, prompt, and answer (non parsons problems also have MC distractors)
class Question:
    problem_type = "generic"
    prompt = "generic question prompt"


# parsons problem, just a reorder question
# answer is just the grouping of lines in the correct order
class Parson(Question):
    def __init__( self, file: File, prompt: str):
        self.id = Path(file.filename).stem.capitalize()
        self.problem_type = "parsons"
        self.prompt = prompt
        self.answer = file.content

# find mutation question: asks which line contains the mutation
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
        # self.answer: str = file.content[mutation.num].code
        self.answer: str = mutation.after
        self.distractors: List[str] = []

        for distractor in distractors:
            if distractor.before != mutation.before:
                self.distractors.append(file.content[distractor.num].code)

        if len(self.distractors) == len(distractors):
            self.distractors.pop()


# classify mutation question: asks what type of mutation was run on this line
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


# fix mutation question: asks what change needs to be made to fix the mutation
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
        self.answer: str = reverse_rep(mutation.replacement).quiz_rep(mutation.after)

        self.distractors: List[str] = []
        for distractor in distractors:
            if distractor.replacement != mutation.replacement:
                self.distractors.append(
                    distractor.replacement.quiz_rep(distractor.before)
                )

        if len(self.distractors) == len(distractors):
            self.distractors.pop()
