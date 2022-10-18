from gift import GIFT
from problem_generator import Quiz
from qti import QTI


# this is a big ol comment
# comment pt 2
def export_file(quiz: Quiz, quiz_format: str, bank_title: str, output_file: str) -> None:
    match quiz_format.lower():
        case "qti":
            qti = QTI(quiz, bank_title, output_file)
            qti.make_quiz()

        case "gift":
            gift = GIFT(quiz, output_file)
            gift.make_quiz()

        case _:
            print(quiz_format.lower())
            print("invalid format name")
