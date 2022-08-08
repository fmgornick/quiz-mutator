import os
import sys

from file import File
from gift import GIFT
from problem_generator import Quiz
from qti import QTI


class QuizMeta:
    def __init__(
        self,
        quiz_title: str = "problem bank", 
        zip_filename: str = "qti", 
        reorder_prompt: str = "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
        find_mutation_prompt: str = "which line contains the mutation?",
        classify_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        fix_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        max_mutations: int = 10,
        mc_distractors: int = 3,
    ):
        self.quiz_title = quiz_title
        self.zip_filename = zip_filename
        self.reorder_prompt = reorder_prompt
        self.find_mutation_prompt = find_mutation_prompt
        self.classify_mutation_prompt = classify_mutation_prompt
        self.fix_mutation_prompt = fix_mutation_prompt
        self.max_mutations = max_mutations
        self.mc_distractors = mc_distractors

def customize_quiz() -> QuizMeta:
    print("\nfor any of the following prompts, just hit enter for default")
    quiz_title = input("quiz title (default = \"problem bank\"): " or "problem bank")
    zip_filename = input("zip filename (default = \"qti\"): " or "qti")
    reorder_prompt = input("reorder prompt: " or  "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.")
    find_mutation_prompt = input("find mutation prompt: " or  "which line contains the mutation?")
    classify_mutation_prompt = input("classify mutation prompt: " or  "what change needs to be made for the function to work properly?")
    fix_mutation_prompt = input("fix mutation prompt: " or  "what change needs to be made for the function to work properly?")
    max_mutations = int(input("max mutations (default = 10, 0 means NO MAX): ") or "10")
    mc_distractors = int(input("number of disractors for mc questions (default = 3): ") or "3")

    return QuizMeta(
        quiz_title = quiz_title,
        zip_filename = zip_filename,
        reorder_prompt = reorder_prompt,
        find_mutation_prompt = find_mutation_prompt,
        classify_mutation_prompt = classify_mutation_prompt,
        fix_mutation_prompt = fix_mutation_prompt,
        max_mutations = max_mutations,
        mc_distractors = mc_distractors,
    )

def format_quiz(quiz: Quiz, format: str, bank_title: str, zip_filename: str) -> None:
    match format.lower():
        case "qti":
            qti = QTI(
                quiz=quiz,
                bank_title=bank_title,
                zip=zip_filename,
            )
            qti.make_quiz()

        case "gift":
            gift = GIFT(
                quiz=quiz,
                zip=zip_filename,
            )
            gift.make_quiz()

        case _:
            print("invalid format name")

if __name__ == "__main__":
    match len(sys.argv):
        case 1:
            print("error: must provide filename argument")

        case 2:
            if os.path.exists(sys.argv[1]):
                format = input("do you want QTI or GIFT format? (default = \"QTI\"): " or "QTI\n")
                yn = input("do you want to customize QTI zip? (y/n): ")
                if (yn == 'y'):
                    meta = customize_quiz()
                else:
                    meta = QuizMeta()
                file = File(sys.argv[1], meta.max_mutations)
                quiz = Quiz(
                    file=file,
                    reorder_prompt=meta.reorder_prompt,
                    find_mutation_prompt=meta.find_mutation_prompt,
                    classify_mutation_prompt=meta.classify_mutation_prompt,
                    fix_mutation_prompt=meta.fix_mutation_prompt,
                    mc_opts=meta.mc_distractors,
                )
                format_quiz(quiz, format, meta.quiz_title, meta.zip_filename)
            else:
                print("error: invalid filename")

        case 3:
            if os.path.exists(sys.argv[1]):
                format = sys.argv[2]
                yn = input("do you want to customize QTI zip? (y/n): ")
                if (yn == 'y'):
                    meta = customize_quiz()
                else:
                    meta = QuizMeta()
                file = File(sys.argv[1], meta.max_mutations)
                quiz = Quiz(
                    file=file,
                    reorder_prompt=meta.reorder_prompt,
                    find_mutation_prompt=meta.find_mutation_prompt,
                    classify_mutation_prompt=meta.classify_mutation_prompt,
                    fix_mutation_prompt=meta.fix_mutation_prompt,
                    mc_opts=meta.mc_distractors,
                )
                format_quiz(quiz, format, meta.quiz_title, meta.zip_filename)
            else:
                print("error: invalid filename")

        case _:
            print("error: invalid number of arguments")
