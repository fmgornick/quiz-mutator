import os
import sys

from export import export_file
from file import File
from problem_generator import Quiz
from quiz_meta import customize_quiz

if __name__ == "__main__":
    try:
        match len(sys.argv):
            # no input - just run the program
            case 1:
                filename = input("file path: ")
                quiz_format = input('do you want QTI or GIFT format? (default = "QTI"): ') or "QTI"
            # filename provided
            case 2:
                filename = sys.argv[1]
                quiz_format = input('do you want QTI or GIFT format? (default = "QTI"): ') or "QTI"
            # filename + file format provided
            case 3:
                filename = sys.argv[1]
                quiz_format = sys.argv[2]
            # incorrect number of arguments
            case _:
                print("error: invalid number of arguments")
                exit()

        if os.path.exists(filename):
            meta = customize_quiz()
            file = File(filename, meta.max_mutations)
            quiz = Quiz(
                file=file,
                reorder_prompt=meta.reorder_prompt,
                find_mutation_prompt=meta.find_mutation_prompt,
                classify_mutation_prompt=meta.classify_mutation_prompt,
                fix_mutation_prompt=meta.fix_mutation_prompt,
                mc_opts=meta.mc_distractors + 1,
            )
            export_file(quiz, quiz_format, meta.quiz_title, meta.zip_filename)
            print("\nfile saved as {}.zip".format(meta.zip_filename))
        else:
            print("error: invalid filename")
    except KeyboardInterrupt:
        print("\nbye!")
        exit()
