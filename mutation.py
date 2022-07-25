import random
from typing import List

from replacement import Replacement
from mutator import Mutator, get_mutators

class Mutation:
    def __init__(
        self,
        mutator_id: str,
        mutator_description: str,
        line_number: int,
        line: str,
        replacement: Replacement,
    ):
        self.id = mutator_id  # name of mutation ran on line
        self.description = mutator_description  # describes mutation
        self.num = line_number  # line number of mutated line
        self.line = line  # line content
        self.replacement = replacement  # info on old and new values


def random_mutator(content: List[str], existing: List[Mutation]) -> Mutation:
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
        line,
        random_replacement(mutator, len(line), line),
    )



def random_replacement(mut: Mutator, length: int, line: str) -> Replacement:
    match mut.mutator_id:
        case "lineDeletion":
            return Replacement(0, length, line, "")

        case "decimalNumberLiteral":
            num = random.random() * 100
            num_len = len("{.2f}".format(num))
            pos = random.randint(0, length-num_len)
            new_line = "%s{.2f}%s".format(line[:pos], num, line[pos+num_len:])
            return random.choice(mut.find_mutations(new_line))

        case "hexNumberLiteral":
            num = random.randint(0, 100)
            num_len = len("0x%d".format(num))
            pos = random.randint(0, length-num_len)
            new_line = "%s0x%d%s".format(line[:pos], num, line[pos+num_len:])
            return random.choice(mut.find_mutations(new_line))

        case _:
            start_col = random.randrange(0, length)
            old_val, new_vals = random.choice(
                list(mut.pattern.replacement_patterns.items())
            )
            new_val = random.choice(new_vals)

            return Replacement(start_col, start_col + len(old_val), old_val, new_val)

