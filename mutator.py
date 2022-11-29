import json
import re
from typing import Dict, List

from replacement import Replacement


# class to locate simple patterns in file to run mutations on
class SimplePattern:
    def __init__(self, replacement_patterns: Dict[str, List[str]]) -> None:
        self.replacement_patterns = replacement_patterns

    # take a line and return all possible replacements for that line
    def mutate(self, line: str) -> List[Replacement]:
        result: List[Replacement] = []

        # for each possible replacement mutation, check to see if the regex
        # pattern is in the line...
        # if so, add the replacement to our list of replacements and return
        for replacement_pattern in self.replacement_patterns.keys():
            for occurrence in [
                match for match in re.finditer(re.compile(replacement_pattern), line)
            ]:
                for replacement_str in self.replacement_patterns[replacement_pattern]:
                    result.append(
                        Replacement(
                            start_col=occurrence.start(),
                            end_col=occurrence.end(),
                            old_val=line[occurrence.start() : occurrence.end()],
                            new_val=replacement_str,
                        )
                    )

        return result

    # for printing
    def __repr__(self) -> str:
        return str(self.replacement_patterns)


# Mutator superclass (doesn't really do anything)
# all mutation classes derive from this and do different things

# all mutator classes after this are pretty self explanatory
# tho, so comments would be a little redundant
class Mutator:
    mutator_id = "mutator"
    description = "generic mutator"
    pattern: SimplePattern

    def find_mutations(self, line: str) -> List[Replacement]:
        return [Replacement(0, 0, "", "")]


class LineDeletion(Mutator):
    mutator_id = "lineDeletion"
    description = "delete whole line"
    tags = ["naive"]

    def __init__(self):
        pass

    def find_mutations(self, line: str) -> List[Replacement]:
        return [Replacement(0, len(line) - 1, line, "")]


class LogicalOperator(Mutator):
    mutator_id = "logicalOperator"
    description = "replace logical operators"
    tags = ["logical", "operator"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " && ": [" || "],
                " and ": [" or "],
                " \|\| ": [" && "],
                " or ": [" and "],
                "!": [""],
                "not": [""],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class ComparisonOperator(Mutator):
    mutator_id = "comparisonOperator"
    description = "replace comparison operators"
    tags = ["operator", "comparison"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " == ": [" != ", " < ", " > ", " <= ", " >= "],
                " != ": [" == ", " < ", " > ", " <= ", " >= "],
                " < ": [" == ", " != ", " > ", " <= ", " >= "],
                " > ": [" == ", " != ", " < ", " <= ", " >= "],
                " <= ": [" == ", " != ", " < ", " > " " >= "],
                " >= ": [" == ", " != ", " < ", " > " " <= "],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class IncDecOperator(Mutator):
    mutator_id = "incDecOperator"
    description = "swap increment and decrement operators"
    tags = ["operator", "artithmetic"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                "\+\+": ["--"],
                "--": ["++"],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class AssignmentOperator(Mutator):
    mutator_id = "assignmentOperator"
    description = "replace assignment operators"
    tags = ["operator"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " = ": [" += ", " -= ", " *= ", " /= ", " %= "],
                " \+= ": [" = ", " -= ", " *= ", " /= ", " %= "],
                " -= ": [" = ", " += ", " *= ", " /= ", " %= "],
                " \*= ": [" = ", " += ", " -= ", " /= ", " %= "],
                " /= ": [" = ", " += ", " -= ", " *= ", " %= "],
                " %= ": [" = ", " += ", " -= ", " *= ", " /= "],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class BooleanAssignmentOperator(Mutator):
    mutator_id = "booleanAssignmentOperator"
    description = "replace boolean assignment operators"
    tags = ["operator", "logical"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " = ": [" &= ", " |= ", " ^= ", " <<= ", " >>= "],
                " &= ": [" = ", " |= ", " ^= ", " <<= ", " >>= "],
                " \|= ": [" = ", " &= ", " ^= ", " <<= ", " >>= "],
                " ^= ": [" = ", " &= ", " |= ", " <<= ", " >>= "],
                " <<= ": [" = ", " &= ", " |= ", " ^= ", " >>= "],
                " >>= ": [" = ", " &= ", " |= ", " ^= ", " <<= "],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class ArithmeticOperator(Mutator):
    mutator_id = "arithmeticOperator"
    description = "replace arithmetic operators"
    tags = ["operator", "artithmetic"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " \+ ": [" - ", " * ", " / ", " % "],
                " - ": [" + ", " * ", " / ", " % "],
                " \* ": [" + ", " - ", " / ", " % "],
                " / ": [" + ", " - ", " * ", " % "],
                " % ": [" + ", " - ", " * ", " / "],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class BooleanArithmeticOperator(Mutator):
    mutator_id = "booleanArithmeticOperator"
    description = "replace boolean arithmetic operators"
    tags = ["operator", "logical"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                " & ": [" | ", " ^ ", " << ", " >> "],
                " \| ": [" & ", " ^ ", " << ", " >> "],
                " ^ ": [" & ", " | ", " << ", " >> "],
                " << ": [" & ", " | ", " ^ ", " >> "],
                " >> ": [" & ", " | ", " ^ ", " << "],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class BooleanLiteral(Mutator):
    mutator_id = "booleanLiteral"
    description = "swap boolean literals"
    tags = ["logical", "literal"]

    def __init__(self):
        self.pattern = SimplePattern({"true": ["false"], "false": ["true"]})

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class StdInserter(Mutator):
    mutator_id = "stdInserter"
    description = "change position where elements are inserted"
    tags = ["stl"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                "std::front_inserter": ["std::back_inserter"],
                "s#td::back_inserter": ["std::front_inserter"],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class StdRangePredicate(Mutator):
    mutator_id = "stdRangePredicate"
    description = "change semantics of an STL range predicate"
    tags = ["stl"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                "std::all_of": ["std::any_of", "std::none_of"],
                "std::any_of": ["std::all_of", "std::none_of"],
                "std::none_of": ["std::all_of", "std::any_of"],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class StdMinMax(Mutator):
    mutator_id = "stdMinMax"
    description = "swap STL minimum and maximum calls"
    tags = ["stl", "artithmetic"]

    def __init__(self):
        self.pattern = SimplePattern(
            {"std::min": ["std::max"], "std::max": ["std::min"]}
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


class DecimalNumberLiteral(Mutator):
    mutator_id = "decimalNumberLiteral"
    description = "replace decimal number literals with different values"
    tags = ["numerical", "literal"]

    def __init__(self):
        self.regex = r"""[^'"a-zA-Z_\\](-?[0-9]+\.?[0-9]*)[^'"a-zA-Z_]?"""

    def find_mutations(self, line: str) -> List[Replacement]:
        result = []  # type: List[Replacement]

        for occurrence in [
            match for match in re.finditer(re.compile(self.regex), line)
        ]:
            number_str = occurrence.group(1)

            # use JSON as means to cope with both int and double
            try:
                number_val = json.loads(number_str)
            except ValueError:
                continue

            replacements = list(
                {number_val + 1, number_val - 1, -number_val, 0} - {number_val}
            )
            for replacement in replacements:
                result.append(
                    Replacement(
                        start_col=occurrence.start(1),
                        end_col=occurrence.end(1),
                        old_val=line[occurrence.start(1):occurrence.end(1)],
                        new_val=str(replacement),
                    )
                )

        return result


class HexNumberLiteral(Mutator):
    mutator_id = "hexNumberLiteral"
    description = "replace hex number literals with different values"
    tags = ["numerical", "literal"]

    def __init__(self):
        self.regex = r"""0[xX][0-9A-Fa-f]+"""

    def find_mutations(self, line: str) -> List[Replacement]:
        result = []  # type: List[Replacement]

        for occurrence in [
            match for match in re.finditer(re.compile(self.regex), line)
        ]:
            number_str = occurrence.group()

            # use JSON as means to cope with both int and double
            number_val = int(number_str, 0)

            replacements = list(
                {number_val + 1, number_val - 1, -number_val, 0} - {number_val}
            )
            for replacement in replacements:
                result.append(
                    Replacement(
                        start_col=occurrence.start(),
                        end_col=occurrence.end(),
                        old_val=line[occurrence.start():occurrence.end()],
                        new_val=hex(replacement),
                    )
                )

        return result


class IteratorRange(Mutator):
    mutator_id = "iteratorRange"
    description = "change iterator range"
    tags = ["iterators"]

    def __init__(self):
        self.pattern = SimplePattern(
            {
                "begin\(\)": ["end()", "begin()+1"],
                "end\(\)": ["end()-1", "end()+1"],
                "std::begin": ["std::end"],
                "std::end": ["std::begin"],
            }
        )

    def find_mutations(self, line: str) -> List[Replacement]:
        return self.pattern.mutate(line)


# returns all possible mutations that we can currently run
# if you want to add your own mutator, make sure to add it's 
# constructor in the mutators list
def get_mutators():
    mutators: List[Mutator] = [
        # LineDeletionMutator(),
        LogicalOperator(),
        ComparisonOperator(),
        IncDecOperator(),
        AssignmentOperator(),
        BooleanAssignmentOperator(),
        ArithmeticOperator(),
        BooleanArithmeticOperator(),
        BooleanLiteral(),
        StdInserter(),
        StdRangePredicate(),
        StdMinMax(),
        DecimalNumberLiteral(),
        HexNumberLiteral(),
        IteratorRange(),
    ]

    return {mutator.mutator_id: mutator for mutator in mutators}
