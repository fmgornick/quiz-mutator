import copy
import re
import xml.dom.minidom as md
from typing import List

import problem_generator as pg


# CLASS:   Moodle
# MEMBERS: generic quiz object + extra meta data for outputted zip
# METHODS: make_quiz
class Moodle:
    # CONSTRUCTOR - assigns arguments and creates template files for QTI formatted zip
    def __init__(self, quiz: pg.Quiz, output: str = "gift"):
        self.quiz = quiz
        self.output = output + ".xml"

        fr = open("templates/moodle/embedded.xml", "r")
        fw = open(self.output, "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

    # called to generate Moodle XML file
    def make_quiz(self):
        match self.quiz.type:
            # if no mutations, then it's just a parsons problem, so generate 1 question
            case "parsons":
                # copy GIFT cloze style template into output file
                file = md.parse(self.output)
                quiz = file.getElementsByTagName("quiz")[0]

                cloze = md.parse("templates/moodle/cloze.xml")
                q_xml = cloze.getElementsByTagName("question")[0]

                q = self.quiz.question

                # format question in basic xml tags
                data: str = "\n"
                data += "<p dir=\"ltr\">" + q.prompt + "</p>\n"
                # every line of parsons problem in each matching question, starts off with no 
                # correct line, then we add credit later
                all_wrong: str = ""
                # tildes used to separate lines in questions, so we must keep track of them
                # to know where to put credit for answers
                tilde_idxs: List[int] = []

                # add each line to our GIFT prompt
                for i, lines in enumerate(q.answer.linegroups):
                    tilde_idxs.append(len(all_wrong))
                    if i != 0:
                        all_wrong += "~"
                    for line in lines:
                        for c in line.comment:
                            all_wrong += moodle_escape(c)
                        all_wrong += moodle_escape(line.code)
                    all_wrong += "#line num should be " + str(i)

                # wrap lines in GIFT question and add credit
                # once done, the lines get added to the CDATA section of our XML file
                for j in range(0, len(q.answer.linegroups)):
                    opt: str = copy.deepcopy(all_wrong)
                    idx = tilde_idxs[j]
                    if j == 0:
                        opt = "%100%" + opt
                    else:
                        opt = opt[:idx+1] + "%100%" + opt[idx+1:]
                    data += "<p dir=\"ltr\">" + str(j) + ") {1:MULTICHOICE:" + opt + "}</p>\n"

                # write data to XML
                cdata = file.createCDATASection(data)
                q_xml.getElementsByTagName("text")[0].appendChild(file.createTextNode("Parsons Problem"))
                q_xml.getElementsByTagName("text")[1].appendChild(cdata)
                quiz.appendChild(q_xml)
                f = open(self.output, "w")
                f.write(file.toprettyxml())
                f.close()

            # if there are mutations, then for each one, generate a new question
            # questions split into three parts for each mutation
            case "mutation":
                ids = ["findMutation", "classifyMutation", "fixMutation"]

                # copy mutation problem template into new file
                fr = open("templates/moodle/embedded.xml", "r")
                fw = open(self.output, "w")
                for line in fr:
                    fw.write(line)
                fr.close()
                fw.close()

                file = md.parse(self.output)
                quiz = file.getElementsByTagName("quiz")[0]

                # for each mutation, add a new cloze question to XML
                for i, set in enumerate(self.quiz.sets):
                    # copy template
                    cloze = md.parse("templates/moodle/cloze.xml")
                    q_xml = cloze.getElementsByTagName("question")[0]

                    data: str = "\n"

                    # question title
                    qtitle = q_xml.getElementsByTagName("text")[0]
                    # question text
                    qtext = q_xml.getElementsByTagName("text")[1]
                    question = "\n"

                    # add all the mutated code to the question prompt so student can see
                    # also format it as code instead of default moodle font
                    for group in set.content.linegroups:
                        for line in group:
                            for c in line.comment:
                                question += "<p><pre><code>" + escape(c) + "</code></pre></p>\n"
                            question += "<p><pre><code>" + escape(line.code) + "</code></pre></p>\n"

                    # add the actual multiple choice questions to the embedded problem
                    for id in ids:
                        data += multiple_choice(set, id)

                    # add changes to file
                    cdata = cloze.createCDATASection(question + "<br>\n" + data)
                    qtitle.appendChild(cloze.createTextNode("Mutation Problem " + str(i)))
                    qtext.appendChild(cdata)
                    quiz.appendChild(q_xml)

                # write to file
                f = open(self.output, "w")
                f.write(file.toprettyxml())
                f.close()

def multiple_choice(set: pg.ProblemSet, mc_field: str) -> str:
    # we want to make sure to pull from the proper question field
    match mc_field:
        case "findMutation":
            field: pg.Question = set.findMutation
        case "classifyMutation":
            field: pg.Question = set.classifyMutation
        case "fixMutation":
            field: pg.Question = set.fixMutation
        case _:
            print("unreachable")
            return ""

    # format MC question as XML to be added to the file's CDATA section
    q: str = "<p dir=\"ltr\">" + field.prompt + "  " + "{1:MULTICHOICE:%100%" 
    # add correct answer
    q += moodle_escape(field.answer) + "#correct!"
    # add incorrect distractors
    for distractor in field.distractors:
        q += "~" + moodle_escape(distractor.strip()) + "#not quite!"
    q += "}</p>\n"

    return q

# basic XML escape sequence macro
def escape(line: str) -> str:
    return re.sub(
        r'(\<|\>)',
        lambda m:{'<':'&lt;','>':'&gt;'}[m.group()],
        line
    )

# moodle XML escape sequence macro
def moodle_escape(line: str) -> str:
    return re.sub(
        r'(\#|\<|\>|\{|\}|~)',
        lambda m:{'#':'\#','<':'&lt;','>':'&gt;','{':'\{','}':'\}','~':'\~'}[m.group()],
        line
    )
