class Replacement:
    def __init__(
        self, start_col: int, end_col: int, old_val: str, new_val: str
    ) -> None:
        self.start_col = start_col
        self.end_col = end_col
        self.old_val = old_val
        self.new_val = new_val

    def apply(self, line: str) -> str:
        # if the whole line is to be replaced, return the new value
        if self.end_col - self.start_col == len(line) - 1:
            return self.new_val

        return "{prefix}{replacement}{suffix}".format(
            prefix=line[: self.start_col],
            replacement=self.new_val,
            suffix=line[self.end_col :],
        )

    def __repr__(self) -> str:
        return '[({begin_col}:{end_col}) "{old_val}" -> "{new_val}"]'.format(
            begin_col=self.start_col,
            end_col=self.end_col,
            old_val=self.old_val,
            new_val=self.new_val,
        )


def reverse(r: Replacement) -> Replacement:
    return Replacement(r.start_col, r.end_col, r.new_val, r.old_val)
