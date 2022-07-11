import os
import shutil
import xml.dom.minidom as md
from typing import List

from mutator import get_mutators
from problem_generator import Quiz
from replacement import Replacement


class QTI:
    def __init__(
        self,
        quiz: Quiz,
        bank_title: str = "question bank",
        zip: str = "qti.zip",
    ):
        self.quiz = quiz
        self.bank_title = bank_title
        self.zip = zip

        os.mkdir("package")
        fr = open("templates/manifest_template.xml", "r")
        fw = open("package/imsmanifest.xml", "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

        fr = open("templates/assessment_template.xml", "r")
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

    def new_section(
        self,
        mutator_id: str,
        section_name: str,
        content: List[str],
        replacement: Replacement,
    ):
        if not os.path.isdir("package/items/" + mutator_id):
            os.mkdir("package/items/" + mutator_id)

        os.mkdir("package/items/" + mutator_id + "/" + section_name)

        mutators = get_mutators()
        mutations = []

        for line in content:
            for _, mutator in mutators.items():
                mutations += mutator.find_mutations(line)

        add_dependencies(mutator_id, section_name, content)
        order(
            mutator_id,
            section_name,
            section_name + " Ordering Problem",
            content,
            self.order_prompt,
        )
        find_mutation(
            mutator_id,
            section_name,
            section_name + " Find Mutation Problem",
            content,
            self.correct,
        )
        fix_mutation(
            mutator_id,
            section_name,
            section_name + " Fix Mutation Problem",
            replacement,
        )

    def make_zip(self, directory, zip="qti"):
        make_pretty(directory)

        shutil.make_archive(zip, "zip", directory)
        shutil.rmtree(directory)


def make_pretty(directory):
    for filename in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, filename)):
            make_pretty(os.path.join(directory, filename))
        else:
            file = md.parse(os.path.join(directory, filename))
            f = open(os.path.join(directory, filename), "w")
            f.write(file.toprettyxml())
            f.close()


def add_dependencies(mutator_id, name, content):
    manifest = md.parse("utils/package/imsmanifest.xml")
    ids = ["Order", "FindMutation", "FixMutation"]

    for id in ids:
        resource = manifest.createElement("resource")
        mhref = manifest.createElement("file")

        resource.setAttribute("identifier", mutator_id + name + id)
        resource.setAttribute("type", "imsqti_item_xmlv2p2")
        resource.setAttribute(
            "href", "items/" + mutator_id + "/" + name + "/" + id + ".xml"
        )

        mhref.setAttribute(
            "href", "items/" + mutator_id + "/" + name + "/" + id + ".xml"
        )

        resource.appendChild(mhref)
        manifest.getElementsByTagName("resources")[0].appendChild(resource)

        dependency = manifest.createElement("dependency")
        dependency.setAttribute("identifierref", mutator_id + name + id)
        manifest.getElementsByTagName("resource")[0].appendChild(dependency)

    f = open("utils/package/imsmanifest.xml", "w")
    f.write(manifest.toxml())
    f.close()

    assessment = md.parse("utils/package/assessment.xml")
    testPart = assessment.getElementsByTagName("testPart")[0]

    section = assessment.createElement("assessmentSection")
    section.setAttribute("identifier", mutator_id + name)
    section.setAttribute("title", mutator_id + " " + name + " section")
    section.setAttribute("visible", "false")

    for id in ids:
        item = assessment.createElement("assessmentItemRef")
        item.setAttribute("identifier", mutator_id + name + id)
        item.setAttribute(
            "href", "items/" + mutator_id + "/" + name + "/" + id + ".xml"
        )

        weight = assessment.createElement("weight")
        weight.setAttribute("identifier", mutator_id + name + id + "Weight")

        if id == "Order":
            weight.setAttribute("value", str(len(content)))
        else:
            weight.setAttribute("value", "2")

        item.appendChild(weight)
        section.appendChild(item)

    testPart.appendChild(section)

    total_lines = int(
        assessment.getElementsByTagName("baseValue")[0].firstChild.nodeValue
    )
    total_lines += len(content)
    assessment.getElementsByTagName("baseValue")[0].firstChild.nodeValue = str(
        total_lines
    )

    f = open("utils/package/assessment.xml", "w")
    f.write(assessment.toxml())
    f.close()


def order(mutator_id, name, question, content, prompt):
    newfile = "utils/package/items/" + mutator_id + "/" + name + "/" + "Order.xml"
    fr = open("utils/templates/order_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute("title", question)
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", mutator_id + name
    )
    file.getElementsByTagName("prompt")[0].appendChild(file.createTextNode(prompt))

    matchIDs = file.getElementsByTagName("correctResponse")[0]
    mapping = file.getElementsByTagName("mapping")[0]
    qLines = file.getElementsByTagName("simpleMatchSet")[0]
    aLines = file.getElementsByTagName("simpleMatchSet")[1]
    for i, line in enumerate(content):
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


def find_mutation(mutator_id, name, question, content, correct):
    newfile = (
        "utils/package/items/" + mutator_id + "/" + name + "/" + "FindMutation.xml"
    )
    fr = open("utils/templates/find_mutation_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute("title", question)
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", mutator_id + name
    )

    if name == "Bubblesort8":
        print(content[1])
        print(correct[1])
    choices = file.getElementsByTagName("choiceInteraction")[0]

    mutators = get_mutators()
    for i, line in enumerate(content):
        for _, mutator in mutators.items():
            if len(mutator.find_mutations(line)) > 0:
                choice = file.createElement("simpleChoice")
                if line != correct[i]:
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


def fix_mutation(mutator_id, name, question, replacement):
    old_val = replacement.new_val
    new_val = replacement.old_val

    newfile = "utils/package/items/" + mutator_id + "/" + name + "/" + "FixMutation.xml"
    fr = open("utils/templates/fix_mutation_template.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    file.getElementsByTagName("assessmentItem")[0].setAttribute("title", question)
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", mutator_id + name
    )

    file.getElementsByTagName("gapText")[0].appendChild(file.createTextNode(old_val))
    file.getElementsByTagName("gapText")[1].appendChild(file.createTextNode(new_val))

    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()
