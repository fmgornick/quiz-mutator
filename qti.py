import os
import shutil
import xml.dom.minidom as md

from mutator import get_mutators
from problem_generator import ProblemSet, Quiz


class QTI:
    def __init__(
        self,
        quiz: Quiz,
        bank_title: str = "question bank",
        zip: str = "qti",
    ):
        self.quiz = quiz
        self.bank_title = bank_title
        self.zip = zip

        os.mkdir("package")
        fr = open("qti_templates/manifest_template.xml", "r")
        fw = open("package/imsmanifest.xml", "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

        fr = open("qti_templates/assessment_template.xml", "r")
        fw = open("package/assessment.xml", "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

        file = md.parse("package/assessment.xml")
        file.getElementsByTagName("assessmentTest")[0].setAttribute(
            "title", self.bank_title
        )
        f = open("package/assessment.xml", "w")
        f.write(file.toxml())
        f.close()

        os.mkdir("package/items")

    def make_quiz(self):
        for set in self.quiz.sets:
            new_section(set)
        make_pretty("package")
        shutil.make_archive(self.zip, "zip", "package")
        shutil.rmtree("package")


def new_section(set: ProblemSet):
    if not os.path.isdir("package/items/" + set.mutation.id):
        os.mkdir("package/items/" + set.mutation.id)

    os.mkdir("package/items/" + set.mutation.id + "/" + set.id)

    add_dependencies(set)
    order(set)
    find_mutation(set)
    fix_mutation(set)


def make_pretty(directory: str):
    for filename in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, filename)):
            make_pretty(os.path.join(directory, filename))
        else:
            file = md.parse(os.path.join(directory, filename))
            f = open(os.path.join(directory, filename), "w")
            f.write(file.toprettyxml())
            f.close()


def add_dependencies(set: ProblemSet):
    manifest = md.parse("package/imsmanifest.xml")
    ids = ["Order", "FindMutation", "FixMutation"]

    for id in ids:
        resource = manifest.createElement("resource")
        mhref = manifest.createElement("file")

        resource.setAttribute("identifier", set.mutation.id + set.id + id)
        resource.setAttribute("type", "imsqti_item_xmlv2p2")
        resource.setAttribute(
            "href", "items/" + set.mutation.id + "/" + set.id + "/" + id + ".xml"
        )

        mhref.setAttribute(
            "href", "items/" + set.mutation.id + "/" + set.id + "/" + id + ".xml"
        )

        resource.appendChild(mhref)
        manifest.getElementsByTagName("resources")[0].appendChild(resource)

        dependency = manifest.createElement("dependency")
        dependency.setAttribute("identifierref", set.mutation.id + set.id + id)
        manifest.getElementsByTagName("resource")[0].appendChild(dependency)

    f = open("package/imsmanifest.xml", "w")
    f.write(manifest.toxml())
    f.close()

    assessment = md.parse("package/assessment.xml")
    testPart = assessment.getElementsByTagName("testPart")[0]

    section = assessment.createElement("assessmentSection")
    section.setAttribute("identifier", set.mutation.id + set.id)
    section.setAttribute("title", set.mutation.id + " " + set.id + " section")
    section.setAttribute("visible", "false")

    for id in ids:
        item = assessment.createElement("assessmentItemRef")
        item.setAttribute("identifier", set.mutation.id + set.id + id)
        item.setAttribute(
            "href", "items/" + set.mutation.id + "/" + set.id + "/" + id + ".xml"
        )

        weight = assessment.createElement("weight")
        weight.setAttribute("identifier", set.mutation.id + set.id + id + "Weight")

        if id == "Order":
            weight.setAttribute("value", str(len(set.content)))
        else:
            weight.setAttribute("value", "2")

        item.appendChild(weight)
        section.appendChild(item)

    testPart.appendChild(section)

    total_lines = int(
        assessment.getElementsByTagName("baseValue")[0].firstChild.nodeValue
    )
    total_lines += len(set.content)
    assessment.getElementsByTagName("baseValue")[0].firstChild.nodeValue = str(
        total_lines
    )

    f = open("package/assessment.xml", "w")
    f.write(assessment.toxml())
    f.close()


def order(set: ProblemSet):
    newfile = "package/items/" + set.mutation.id + "/" + set.id + "/" + "Order.xml"
    fr = open("qti_templates/order_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "title", set.id + " Ordering Problem"
    )
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", set.mutation.id + set.id
    )
    file.getElementsByTagName("prompt")[0].appendChild(
        file.createTextNode(set.reorder.prompt)
    )

    matchIDs = file.getElementsByTagName("correctResponse")[0]
    mapping = file.getElementsByTagName("mapping")[0]
    qLines = file.getElementsByTagName("simpleMatchSet")[0]
    aLines = file.getElementsByTagName("simpleMatchSet")[1]
    for i, line in enumerate(set.content):
        matchID = file.createElement("value")
        matchID.appendChild(file.createTextNode("q" + str(i + 1) + " a" + str(i + 1)))

        map = file.createElement("mapEntry")
        map.setAttribute("mapKey", "q" + str(i + 1) + " a" + str(i + 1))
        map.setAttribute("mappedValue", "1")
        mapping.appendChild(map)

        qLine = file.createElement("simpleAssociableChoice")
        qLine.setAttribute("identifier", "q" + str(i + 1))
        qLine.setAttribute("matchMax", "1")
        qLine.appendChild(file.createTextNode(str(i + 1)))

        aLine = file.createElement("simpleAssociableChoice")
        aLine.setAttribute("identifier", "a" + str(i + 1))
        aLine.setAttribute("matchMax", "1")
        aLine.appendChild(file.createTextNode(line))

        matchIDs.appendChild(matchID)
        qLines.appendChild(qLine)
        aLines.appendChild(aLine)

    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()


def find_mutation(set: ProblemSet):
    newfile = (
        "package/items/" + set.mutation.id + "/" + set.id + "/" + "FindMutation.xml"
    )
    fr = open("qti_templates/find_mutation_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "title", set.id + " Find Mutation Problem"
    )
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", set.mutation.id + set.id
    )

    choices = file.getElementsByTagName("choiceInteraction")[0]

    mutators = get_mutators()
    for i, line in enumerate(set.content):
        for _, mutator in mutators.items():
            if len(mutator.find_mutations(line)) > 0:
                choice = file.createElement("simpleChoice")
                if line != set.findMutation.answer[i]:
                    choice.setAttribute("identifier", "correct")
                else:
                    choice.setAttribute("identifier", "wrong" + str(i))

                choice.setAttribute("fixed", "false")
                choice.appendChild(file.createTextNode(line))

                choices.appendChild(choice)

                break

    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()


def fix_mutation(set: ProblemSet):

    newfile = (
        "package/items/" + set.mutation.id + "/" + set.id + "/" + "FixMutation.xml"
    )
    fr = open("qti_templates/fix_mutation_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "title", set.id + " Fix Mutation Problem"
    )
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", set.mutation.id + set.id
    )

    file.getElementsByTagName("gapText")[0].appendChild(
        file.createTextNode(set.fixMutation.answer.old_val)
    )
    file.getElementsByTagName("gapText")[1].appendChild(
        file.createTextNode(set.fixMutation.answer.old_val)
    )

    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()
