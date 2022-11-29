import os
import shutil
import xml.dom.minidom as md

import problem_generator as pg
from line import LineGroup


# CLASS:   Canvas
# MEMBERS: generic quiz object + extra meta data for outputted zip
# METHODS: make_quiz
class Canvas:
    # CONSTRUCTOR - assigns arguments and creates template files for QTI formatted zip
    def __init__(
        self,
        quiz: pg.Quiz,
        bank_title: str = "question bank",
        output: str = "qti",
    ):
        self.quiz = quiz
        self.bank_title = bank_title
        self.zip = output

        os.mkdir("package")
        fr = open("templates/canvas/manifest.xml", "r")
        fw = open("package/imsmanifest.xml", "w")
        for line in fr:
            fw.write(line)
        fr.close()
        fw.close()

        fr = open("templates/canvas/assessment.xml", "r")
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

        if quiz.type == "mutation":
            os.mkdir("package/items")

    # called to generate QTI formatted zip file
    def make_quiz(self):
        match self.quiz.type:
            # if no mutations, then it's just a parsons problem, so generate 1 question
            case "parsons":
                make_parsons(self.quiz.question)
            # if there are mutations, then for each one, generate a new section of questions
            # Find / Classify / Fix Mutation
            case "mutation":
                for set in self.quiz.sets:
                    new_section(set)
        # once all the files generated, turn them into a zip and remove the directory
        make_pretty("package")
        shutil.make_archive(self.zip, "zip", "package")
        shutil.rmtree("package")


# go through each generated file and add spacing to the lines so it has a neater output
# not necessary, but nice for debugging
def make_pretty(directory: str):
    for filename in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, filename)):
            make_pretty(os.path.join(directory, filename))
        else:
            file = md.parse(os.path.join(directory, filename))
            f = open(os.path.join(directory, filename), "w")
            f.write(file.toprettyxml())
            f.close()


# create new mutation section with 3 problem types
def new_section(set: pg.ProblemSet):
    if not os.path.isdir("package/items/" + set.mutation.id):
        os.mkdir("package/items/" + set.mutation.id)

    os.mkdir("package/items/" + set.mutation.id + "/" + set.id)

    add_dependencies(set)
    multiple_choice(set, "findMutation")
    multiple_choice(set, "classifyMutation")
    multiple_choice(set, "fixMutation")


# imsmanifest.xml and assessment.xml are both used to store meta data about the quiz, so 
# this function does just that
def add_dependencies(set: pg.ProblemSet):
    manifest = md.parse("package/imsmanifest.xml")
    ids = ["FindMutation", "ClassifyMutation", "FixMutation"]

    ######################## ADD TO IMSMANIFEST.XML ########################
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
    ########################################################################

    ######################## ADD TO ASSESSMENT.XML #########################
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
        section.appendChild(item)

    testPart.appendChild(section)

    f = open("package/assessment.xml", "w")
    f.write(assessment.toxml())
    f.close()
    ########################################################################

# create the parsons problem using the QTI ordering question style
def make_parsons(question: pg.Parson):
    # adding adding dependencies for parsons problem done separately

    ############################ ADD DEPENDENCIES ##########################
    manifest = md.parse("package/imsmanifest.xml")

    resource = manifest.createElement("resource")
    mhref = manifest.createElement("file")

    resource.setAttribute("identifier", question.id)
    resource.setAttribute("type", "imsqti_item_xmlv2p2")
    resource.setAttribute("href", "Parsons.xml")
    mhref.setAttribute("href", "Parsons.xml")

    resource.appendChild(mhref)
    manifest.getElementsByTagName("resources")[0].appendChild(resource)

    dependency = manifest.createElement("dependency")
    dependency.setAttribute("identifierref", question.id)
    manifest.getElementsByTagName("resource")[0].appendChild(dependency)

    f = open("package/imsmanifest.xml", "w")
    f.write(manifest.toxml())
    f.close()

    assessment = md.parse("package/assessment.xml")
    testPart = assessment.getElementsByTagName("testPart")[0]

    section = assessment.createElement("assessmentSection")
    section.setAttribute("identifier", question.id)
    section.setAttribute("title", question.id + " Parsons Problem")
    section.setAttribute("visible", "false")

    item = assessment.createElement("assessmentItemRef")
    item.setAttribute("identifier", question.id)
    item.setAttribute("href", "Parsons.xml")
    section.appendChild(item)

    testPart.appendChild(section)

    f = open("package/assessment.xml", "w")
    f.write(assessment.toxml())
    f.close()
    ########################################################################

    # copy parsons problem template into new file
    newfile = "package/Parsons.xml"
    fr = open("templates/canvas/parsons.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    # question title
    file : md.Document = md.parse(newfile)
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "title", question.id + " Parsons Problem"
    )
    # question prompt
    file.getElementsByTagName("prompt")[0].appendChild(
        file.createTextNode(question.prompt)
    )

    # add each line of file to XML Ordering Question, with identifier to 
    # keep track of order
    orderIDs = file.getElementsByTagName("correctResponse")[0]
    orderLines = file.getElementsByTagName("orderInteraction")[0]
    for i, group in enumerate(question.answer.linegroups):
        orderID = file.createElement("value")
        orderID.appendChild(file.createTextNode("line" + str(i)))

        orderLine = file.createElement("simpleChoice")
        orderLine.setAttribute("identifier", "line" + str(i))
        
        orderPar : md.Element = file.createElement("")
        orderCode : md.Element = file.createElement("")
        for line in group:
            for c in line.comment:
                orderPar = file.createElement("p")
                orderCode = file.createElement("code")
                orderCode.appendChild(file.createTextNode(c))
                orderPar.appendChild(orderCode)
                orderLine.appendChild(orderPar)

            orderPar = file.createElement("p")
            orderCode = file.createElement("code")
            orderCode.appendChild(file.createTextNode(line.code))
            orderPar.appendChild(orderCode)
            orderLine.appendChild(orderPar)

        orderIDs.appendChild(orderID)
        orderLines.appendChild(orderLine)

    # write changes
    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()


# for mutation problems we generate 3 MC questions per mutation, this
# function is called 3 times for each mutation with different question types
def multiple_choice(set: pg.ProblemSet, mc_field: str) -> None:
    # depending on the question type, we want the title and file to differ
    match mc_field:
        case "findMutation":
            field: pg.Question = set.findMutation
            title: str = " Find Mutation Problem"
            filename: str = "FindMutation.xml"
        case "classifyMutation":
            field: pg.Question = set.classifyMutation
            title: str = " Classify Mutation Problem"
            filename: str = "ClassifyMutation.xml"
        case "fixMutation":
            field: pg.Question = set.fixMutation
            title: str = " Fix Mutation Problem"
            filename: str = "FixMutation.xml"
        case _:
            print("unreachable")
            return

    # copy template into new file
    newfile = "package/items/" + set.mutation.id + "/" + set.id + "/" + filename
    fr = open("templates/canvas/mc.xml", "r")
    fw = open(newfile, "w")
    for line in fr:
        fw.write(line)
    fr.close()
    fw.close()

    file = md.parse(newfile)

    # tilte
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "title", set.id + title
    )
    # question ID
    file.getElementsByTagName("assessmentItem")[0].setAttribute(
        "identifier", set.mutation.id + set.id
    )
    # prompt
    prompt = file.getElementsByTagName("prompt")[0]
    show_code(file, prompt, set.content)
    prompt.appendChild(file.createTextNode(field.prompt))

    choices = file.getElementsByTagName("choiceInteraction")[0]

    # set correct answer
    correct = file.createElement("simpleChoice")
    correct.setAttribute("fixed", "false")
    correct.setAttribute("identifier", "correct")
    correct.appendChild(file.createTextNode(field.answer))
    choices.appendChild(correct)

    # set distractor choices
    for distractor in field.distractors:
        wrong = file.createElement("simpleChoice")
        wrong.setAttribute("fixed", "false")
        wrong.setAttribute("identifier", "wrong")
        wrong.appendChild(file.createTextNode(distractor))
        choices.appendChild(wrong)

    # write changes
    f = open(newfile, "w")
    f.write(file.toxml())
    f.close()


# displays code of file in question as code, instead of Canvas's default font
def show_code(file: md.Document, element: md.Element, content: LineGroup):
    orderPar : md.Element = file.createElement("")
    orderCode : md.Element = file.createElement("")
    for group in content.linegroups:
        for l in group:
            orderPar = file.createElement("p")
            orderPre = file.createElement("pre")
            orderCode = file.createElement("code")
            orderCode.appendChild(file.createTextNode(l.code))
            orderPre.appendChild(orderCode)
            orderPar.appendChild(orderPre)
            element.appendChild(orderPar)
        element.appendChild(file.createElement("p"))
