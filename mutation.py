import random
from typing import List

from line import Line
from mutator import Mutator, get_mutators
from replacement import Replacement


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
        self.id: str = mutator_id                         # name of mutation ran on line
        self.description: str = description               # describes mutation
        self.num: int = line_num                          # line number of mutated line
        self.before: str = line                           # line content before mutation
        self.after: str = replacement.apply(self.before)  # line content after mutation
        self.replacement: Replacement = replacement       # info on old and new values

    # for printing mutation (mainly used for debugging)
    def __repr__(self) -> str:
        return 'mutator id: {id}\ndescription: {des}\nline: {line}\nreplacement: {rep}\n'.format(
            id=self.id,
            des=self.description,
            line=self.before,
            rep=self.replacement,
        )

# function used to create a random mutation on a file, used as a distractor
# for a multiple choice question
# TODO: change up logic of mutation generator function
def random_mutation(content: List[Line], existing: List[Mutation]) -> Mutation:
    mutators = get_mutators()
    unused_mutators = get_mutators()
    for mut in existing:
        del(unused_mutators[mut.id])

    mutator: Mutator

    if len(unused_mutators) == 0:
        mutator = random.choice(list(mutators.values()))
    else:
        mutator = random.choice(list(unused_mutators.values()))

    line_num = random.randrange(len(content))
    line = content[line_num]

    return Mutation(
        mutator.mutator_id,
        mutator.description,
        line_num,
        line.code,
        random_replacement(mutator, line.code),
    )



# apply random replacement on a given line with specified mutator
def random_replacement(mut: Mutator, line: str) -> Replacement:
    match mut.mutator_id:
        case "lineDeletion":
            return Replacement(0, len(line), line, "")

        case "decimalNumberLiteral":
            num = random.random() * 100
            num_len = len("%.2f".format(num))
            pos = random.randrange(0, len(line)-num_len)
            new_line = "%s%.2f%s".format(line[:pos], num, line[pos+num_len:])
            return random.choice(mut.find_mutations(new_line))

        case "hexNumberLiteral":
            num = random.randint(0, 100)
            num_len = len("0x%d".format(num))
            pos = random.randrange(0, len(line)-num_len)
            new_line = "%s0x%d%s".format(line[:pos], num, line[pos+num_len:])
            return random.choice(mut.find_mutations(new_line))

        case _:
            start_col = random.randrange(0, len(line))
            old_val, new_vals = random.choice(
                list(mut.pattern.replacement_patterns.items())
            )
            new_val = random.choice(new_vals)

            return Replacement(start_col, start_col + len(old_val), old_val, new_val)
