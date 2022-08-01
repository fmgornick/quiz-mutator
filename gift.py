import os
import shutil
from pathlib import Path

import problem_generator as pg


class GIFT:
    def __init__(self, quiz: pg.Quiz, zip: str = "gift"):
        self.quiz = quiz
        self.zip = zip

        os.mkdir("package")

    def make_quiz(self):
        for set in self.quiz.sets:
            new_section(set)
        shutil.make_archive(self.zip, "zip", "package")
        shutil.rmtree("package")


def new_section(set: pg.ProblemSet):
    filename = "package/" + set.id + ".txt"
    Path(filename).touch()
    order(set, filename)
    multiple_choice(set, filename, "findMutation")
    multiple_choice(set, filename, "classifyMutation")
    multiple_choice(set, filename, "fixMutation")


def order(set: pg.ProblemSet, filename: str):
    f = open(filename, "a")
    f.write("::" + set.id + " Ordering Problem\n")
    f.write("::" + set.order.prompt + " {\n")

    for i, line in enumerate(set.order.answer):
        f.write("\t={num} -> {line}\n".format(num=i, line=line))
    f.write("}\n\n")
    f.close()

def multiple_choice(set: pg.ProblemSet, filename: str, mc_field: str):
    match mc_field:
        case "findMutation":
            field: pg.Question = set.findMutation
            title: str = " Find Mutation Problem"
        case "classifyMutation":
            field: pg.Question = set.classifyMutation
            title: str = " Classify Mutation Problem"
        case "fixMutation":
            field: pg.Question = set.fixMutation
            title: str = " Fix Mutation Problem"
        case _:
            print("unreachable")
            return

    f = open(filename, "a")
    f.write("::" + set.id + title + "\n")
    f.write("::" + field.prompt + " {\n")
    f.write("\t=" + field.answer + "\n")
    for distractor in field.distractors:
        f.write("\t~" + distractor + "\n")
    f.write("}\n\n")
    f.close()
