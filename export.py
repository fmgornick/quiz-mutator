from canvas import Canvas
from moodle import Moodle
from problem_generator import Quiz


# this is a big ol comment
# comment pt 2
def export_file(quiz: Quiz, quiz_format: str, bank_title: str, output_file: str) -> None:
    match quiz_format.lower():
        case "canvas":
            qti = Canvas(quiz, bank_title, output_file)
            qti.make_quiz()

        case "moodle":
            gift = Moodle(quiz, output_file)
            gift.make_quiz()

        case _:
            print(quiz_format.lower())
            print("invalid format name")
