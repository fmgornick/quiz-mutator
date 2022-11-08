import os
import shutil
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
                quiz_format = input("canvas (QTI) or moodle (Moodle XML) format? (default = \"canvas\"): ") or "canvas"
            # filename provided
            case 2:
                filename = sys.argv[1]
                quiz_format = input("canvas (QTI) or moodle (Moodle XML) format? (default = \"canvas\"): ") or "canvas"
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
            file = File(filename, meta)
            quiz = Quiz(file, meta)
            export_file(quiz, quiz_format, meta.quiz_title, meta.output_file)
            print("\nfile saved as {}.{}".format(meta.output_file, "zip" if quiz_format.lower() == "canvas" else "xml"))
        else:
            print("error: invalid filename")
    except KeyboardInterrupt:
        print("\nbye!")
        exit()
    except BaseException as err:
        print(f"ERROR: {err=}, {type(err)=}")
        if os.path.exists("package"):
            print("removing package directory...")
            shutil.rmtree("package", ignore_errors=True)
        raise
