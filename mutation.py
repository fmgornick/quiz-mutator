from replacement import Replacement, reverse_rep


# mutation object: contains information about a mutation ran on a specific file
# object contains id, description, line number, replacement made, and a before->after
class Mutation:
    def __init__(
        self,
        mutator_id: str,
        description: str,
        line_num: int,
        line: str,
        replacement: Replacement,
    ):
        self.id: str = mutator_id  # name of mutation ran on line
        self.description: str = description  # describes mutation
        self.num: int = line_num  # line number of mutated line
        self.before: str = line  # line content before mutation
        self.after: str = replacement.apply(self.before)  # line content after mutation
        self.replacement: Replacement = replacement  # info on old and new values

    # for printing mutation (mainly used for debugging)
    def __repr__(self) -> str:
        return "mutator id: {id}\ndescription: {des}\nline: {line}\nreplacement: {rep}\n".format(
            id=self.id,
            des=self.description,
            line=self.before,
            rep=self.replacement,
        )


def reverse_mut(m: Mutation) -> Mutation:
    return Mutation(
        mutator_id=m.id,
        description=m.description,
        line_num=m.num,
        line=m.after,
        replacement=reverse_rep(m.replacement),
    )
