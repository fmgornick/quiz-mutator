from file import File
from problem_generator import Quiz
from qti import QTI

if __name__ == "__main__":
    file = File("main.py", 5)
    quiz = Quiz(file)
    qti = QTI(quiz)
    qti.make_quiz()
