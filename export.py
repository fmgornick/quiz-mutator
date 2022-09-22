from gift import GIFT
from problem_generator import Quiz
from qti import QTI


def export_file(quiz: Quiz, quiz_format: str, bank_title: str, zip_filename: str) -> None:
    match quiz_format.lower():
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
            print(quiz_format.lower())
            print("invalid format name")
