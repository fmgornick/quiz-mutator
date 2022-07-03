from file import File
from replacement import Replacement


class MutatedFile:
    def __init__(
        self, file: File, rep: Replacement, mutator_id: str, line: int
    ) -> None:
        self.file = file
        self.file.content[line] = rep.apply(self.file.content[line])
        self.line = line
        self.replacement = rep
        self.id = mutator_id
