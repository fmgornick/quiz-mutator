from typing import List


class Line:
    def __init__(self, code: str, comment: List[str]):
        self.code = code
        self.comment = comment

    def __repr__(self) -> str:
        line = ""
        for c in self.comment:
            line += c
        line += self.code
        return line
