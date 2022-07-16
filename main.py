from mutation_generator import MutatedFiles
from problem_generator import Quiz
from qti import QTI

if __name__ == "__main__":
    files = MutatedFiles("main.py")
    quiz = Quiz(files)
    qti = QTI(quiz)
    qti.make_quiz()
