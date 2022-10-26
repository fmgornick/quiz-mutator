import os
from typing import List

from termcolor import colored


class Line:
    def __init__(self, code: str, comment: List[str]):
        self.code = code
        self.comment = comment
        self.numlines = len(comment) + 1

    def __repr__(self) -> str:
        line = ""
        for c in self.comment:
            line += c + "\n"
        line += self.code
        return line


class LineGroup:
    def __init__(self, lines: List[Line], groupings: List[List[int]]):
        self.linegroups: List[List[Line]] = []

        for i, group in enumerate(groupings):
            self.linegroups.append([])
            for line_num in group:
                self.linegroups[i].append(lines[line_num])

    def __getitem__(self, idx: int) -> Line:
        curr: int = 0
        for group in self.linegroups:
            for line in group:
                if curr == idx:
                    return line
                else:
                    curr += 1

        raise IndexError


def group_lines(lines: List[Line]) -> LineGroup:
    userin: str = ""
    groupings: List[List[int]] = []
    flattened_groups: List[int] = []
    while True:
        print("----------------------------------------")
        print("1) line groupings should be contiguous")
        print("2) separate line numbers by spaces")
        print("3) changes cannot be undone")
        print('4) press "q" or <enter> to quit grouping')
        print("----------------------------------------")
        if len(groupings) > 0:
            flattened_groups = [i for group in groupings for i in group]
        print()
        for i, l in enumerate(lines):
            if i in flattened_groups:
                print("x\t{}".format(l.code))
            else:
                print("{}\t{}".format(i, l.code))

        userin = input("\nlines to group: ") or "q"
        if userin == "q":
            break

        try:
            nums = [int(num) for num in userin.split()]
        except ValueError:
            os.system("clear")
            print(colored("ERROR: must input ints separated by space\n", "yellow"))
            continue

        nums.sort()
        if nums != list(range(min(nums), max(nums) + 1)):
            os.system("clear")
            print(colored("ERROR: not contiguous\n", "yellow"))
            continue

        bad_idx: bool = False
        for num in nums:
            if num in flattened_groups or num < 0 or num >= len(lines):
                os.system("clear")
                print(colored("ERROR: index not available\n", "yellow"))
                bad_idx = True
                break

        if not bad_idx:
            groupings.append(nums)
            os.system("clear")

    for i, _ in enumerate(lines):
        if i not in flattened_groups:
            groupings.append([i])
    print(sorted(groupings, key=lambda x: x[0]))
    return LineGroup(lines, sorted(groupings, key=lambda x: x[0]))
