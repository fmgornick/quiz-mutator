# CLASS:   Replacement
# MEMBERS: start col - first index of repleced sequence
#          end col   - last index of repleced sequence
#          old val   - substring before replacement
#          new val   - substring after replacement
# METHODS: apply, quiz_rep
class Replacement:
    def __init__(
        self, start_col: int, end_col: int, old_val: str, new_val: str
    ) -> None:
        self.start_col = start_col
        self.end_col = end_col
        self.old_val = old_val
        self.new_val = new_val

    # takes a string and replaces the old value with the new value at the specified line
    def apply(self, line: str) -> str:
        # if the whole line is to be replaced, return the new value
        if self.end_col - self.start_col == len(line) - 1:
            return self.new_val

        return "{prefix}{replacement}{suffix}".format(
            prefix=line[: self.start_col],
            replacement=self.new_val,
            suffix=line[self.end_col :],
        )

    # for printing the replacement
    def __repr__(self) -> str:
        return '[({begin_col}:{end_col}) "{old_val}" -> "{new_val}"]'.format(
            begin_col=self.start_col,
            end_col=self.end_col,
            old_val=self.old_val,
            new_val=self.new_val,
        )

    # for representing the replacement in fix mutation prompt
    def quiz_rep(self, line: str) -> str:
        return (
            '[({begin_col}:{end_col}) "{old_val}" -> "{new_val}"] in "{line}"'.format(
                line=line.strip(),
                begin_col=self.start_col,
                end_col=self.end_col,
                old_val=self.old_val,
                new_val=self.new_val,
            )
        )


# returns exact opposite replacement
# used for generating multiple choice distractors
def reverse_rep(r: Replacement) -> Replacement:
    return Replacement(r.start_col, r.end_col, r.new_val, r.old_val)
