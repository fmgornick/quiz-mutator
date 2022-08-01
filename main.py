from file import File
from gift import GIFT
from problem_generator import Quiz
from qti import QTI

if __name__ == "__main__":
    file = File("main.py", 5)
    quiz = Quiz(file)
    qti = GIFT(quiz)
    qti.make_quiz()
