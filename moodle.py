import copy
import os
import xml.dom.minidom as md
from typing import List
# import re
from xml.sax.saxutils import escape

import problem_generator as pg

# from xml.sax.saxutils import escape



class Moodle:
    def __init__(self, quiz: pg.Quiz, output: str = "gift"):
        self.quiz = quiz
        self.output = output + ".xml"

        fr = open("templates/moodle/embedded.xml", "r")
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

                for i, lines in enumerate(q.answer.linegroups):
                    tilde_idxs.append(len(all_wrong))
                    if i != 0:
                        all_wrong += "~"
                    for line in lines:
                        for c in line.comment:
                            all_wrong += escape(c)
                        all_wrong += escape(line.code)
                    all_wrong += "#line num should be " + str(i)

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
                ids = ["findMutation", "classifyMutation", "fixMutation"]
                os.mkdir("package")
                for i, set in enumerate(self.quiz.sets):
                    fname = "package/" + set.id + ".xml"
                    fr = open("templates/moodle/embedded.xml", "r")
                    fw = open(fname, "w")
                    for line in fr:
                        fw.write(line)
                    fr.close()
                    fw.close()

                    file = md.parse(fname)
                    # q = self.quiz.question

                    data: str = "\n"
                    all_wrong: str = ""
                    tilde_idxs: List[int] = []

                    qtitle = file.getElementsByTagName("text")[0]
                    qtext = file.getElementsByTagName("text")[1]
                    question = "\n"

                    for group in set.content.linegroups:
                        for line in group:
                            for c in line.comment:
                                question += "<p><pre><code>" + escape(c) + "</code></pre></p>\n"
                            question += "<p><pre><code>" + escape(line.code) + "</code></pre></p>\n"

                    for id in ids:
                        data += multiple_choice(set, id)

                    cdata = file.createCDATASection(question + "<br>\n" + data)
                    qtitle.appendChild(file.createTextNode("Mutation Problem " + str(i)))
                    qtext.appendChild(cdata)
                    f = open(fname, "w")
                    f.write(file.toprettyxml())
                    f.close()

def multiple_choice(set: pg.ProblemSet, mc_field: str) -> str:
    match mc_field:
        case "findMutation":
            field: pg.Question = set.findMutation
            # title: str = " Find Mutation Problem"
        case "classifyMutation":
            field: pg.Question = set.classifyMutation
            # title: str = " Classify Mutation Problem"
        case "fixMutation":
            field: pg.Question = set.fixMutation
            # title: str = " Fix Mutation Problem"
        case _:
            print("unreachable")
            return ""

    q: str = "<p dir=\"ltr\">" + field.prompt + "  " + "{1:MULTICHOICE:%100%" 
    q += escape(field.answer) + "#correct!"
    for distractor in field.distractors:
        q += "~" + escape(distractor) + "#not quite!"
    q += "}</p>\n"

    return q

# def escape(line: str) -> str:
#     return re.sub(
#         r'(\#|\<|\>)',
#         lambda m:{'#':'&num;','<':'&lt;','>':'&gt;'}[m.group()],
#         line
#     )
