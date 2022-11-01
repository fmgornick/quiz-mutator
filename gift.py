import copy
import re
import xml.dom.minidom as md
from typing import List, TextIO

import problem_generator as pg


class GIFT:
    def __init__(self, quiz: pg.Quiz, output: str = "gift"):
        self.quiz = quiz
        self.output = output + ".xml"

        fr = open("qti_templates/gift_order.xml", "r")
        fw = open(self.output, "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

    def make_quiz(self):
        match self.quiz.type:
            case "parsons":
                file = md.parse(self.output)
                q = self.quiz.question

                data: str = "\n"
                all_wrong: str = ""
                tilde_idxs: List[int] = []

                for j, lines in enumerate(q.answer.linegroups):
                    tilde_idxs.append(len(all_wrong))
                    if j != 0:
                        all_wrong += "~"
                    for line in lines:
                        for c in line.comment:
                            all_wrong += escape(c)
                        all_wrong += escape(line.code)
                    all_wrong += "#line num should be " + str(j)

                for j in range(0, len(q.answer.linegroups)):
                    opt: str = copy.deepcopy(all_wrong)
                    idx = tilde_idxs[j]
                    if j == 0:
                        opt = "%100%" + opt
                    else:
                        opt = opt[:idx+1] + "%100%" + opt[idx+1:]
                    data += "<p dir=\"ltr\">" + str(j) + ") {1:MULTICHOICE:" + opt + "}</p>\n"

                cdata = file.createCDATASection(data)
                file.getElementsByTagName("text")[0].appendChild(file.createTextNode(q.prompt))
                file.getElementsByTagName("text")[1].appendChild(cdata)
                f = open(self.output, "w")
                f.write(file.toprettyxml())
                f.close()

            case "mutation":
                f = open(self.output, "a")
                for set in self.quiz.sets:
                    # order(set, f)
                    multiple_choice(set, f, "findMutation")
                    multiple_choice(set, f, "classifyMutation")
                    multiple_choice(set, f, "fixMutation")
                    f.write("\n\n")
                f.close()

def multiple_choice(set: pg.ProblemSet, f: TextIO, mc_field: str):
    match mc_field:
        case "findMutation":
            field: pg.Question = set.findMutation
            title: str = " Find Mutation Problem"
        case "classifyMutation":
            field: pg.Question = set.classifyMutation
            title: str = " Classify Mutation Problem"
        case "fixMutation":
            field: pg.Question = set.fixMutation
            title: str = " Fix Mutation Problem"
        case _:
            print("unreachable")
            return

    f.write("::" + escape(set.id) + escape(title) + "\n")
    f.write("::" + escape(field.prompt) + " {\n")
    f.write("\t=" + escape(field.answer) + "\n")
    for distractor in field.distractors:
        f.write("\t~" + escape(distractor) + "\n")
    f.write("}\n\n")

def escape(line: str) -> str:
    return re.sub(
        # r'(\~|\=|\#|\{|\}|\:)',
        # lambda m:{'~':'\~','=':'\=','#':'\#','{':'\{','}':'\}',':':'\:'}[m.group()],
        r'(\~|\#|\}|\:)|\<|\>',
    lambda m:{'~':'\~','#':'\#','}':'\}',':':'\:','<':'&lt;','>':'&gt;'}[m.group()],
        line
    )
