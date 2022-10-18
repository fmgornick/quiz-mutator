class QuizMeta:
    def __init__(
        self,
        quiz_title: str,
        output_file: str,
        type: str,
        reorder_prompt: str,
        find_mutation_prompt: str = "",
        classify_mutation_prompt: str = "",
        fix_mutation_prompt: str = "",
        max_mutations: int = 0,
        mc_distractors: int = 0,
    ):
        self.quiz_title = quiz_title
        self.output_file = output_file
        self.type = type
        self.reorder_prompt = reorder_prompt

        if type == "mutation":
            self.find_mutation_prompt = find_mutation_prompt
            self.classify_mutation_prompt = classify_mutation_prompt
            self.fix_mutation_prompt = fix_mutation_prompt
            self.max_mutations = max_mutations
            self.mc_distractors = mc_distractors
            self.format = "mutation"


def customize_quiz() -> QuizMeta:
    just_parsons = input("do you want to add mutations to the file? (y/n): ") != "y"
    yn = input("do you want to customize your output file? (y/n): ") == "y"
    if yn:
        print("\nfor any of the following prompts, just hit enter for default...")
        quiz_title = input('quiz title (default = "problem bank"): ') or "problem bank"

        output_file = (
            input('output file (default = "problem_bank"): ').replace(" ", "_")
            or "problem_bank"
        )

        if just_parsons:
            reorder_prompt = (
                input("reorder prompt: ") or "correct the order of these lines."
            )

            return QuizMeta(
                quiz_title=quiz_title,
                output_file=output_file,
                type="parsons",
                reorder_prompt=reorder_prompt,
            )

        else:
            reorder_prompt = (
                input("reorder prompt: ")
                or "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now."
            )

            find_mutation_prompt = (
                input("find mutation prompt: ") or "which line contains the mutation?"
            )

            classify_mutation_prompt = (
                input("classify mutation prompt: ") or "what did this mutation do?"
            )

            fix_mutation_prompt = (
                input("fix mutation prompt: ")
                or "what change needs to be made for the function to work properly?"
            )

            max_mutations = int(
                input("max mutations (default = 10, 0 means NO MAX): ") or "10"
            )

            mc_distractors = int(
                input("number of disractors for mc questions (default = 3): ") or "3"
            )

            return QuizMeta(
                quiz_title=quiz_title,
                output_file=output_file,
                type="mutation",
                reorder_prompt=reorder_prompt,
                find_mutation_prompt=find_mutation_prompt,
                classify_mutation_prompt=classify_mutation_prompt,
                fix_mutation_prompt=fix_mutation_prompt,
                max_mutations=max_mutations,
                mc_distractors=mc_distractors,
            )
    else:
        if just_parsons:
            return QuizMeta(
                quiz_title="problem bank",
                output_file="problem_bank",
                type="parsons",
                reorder_prompt="correct the order of these lines.",
            )
        else:
            return QuizMeta(
                quiz_title="problem bank",
                output_file="problem_bank",
                type="mutation",
                reorder_prompt="correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
                find_mutation_prompt="which line contains the mutation?",
                classify_mutation_prompt="what did this mutation do?",
                fix_mutation_prompt="what change needs to be made for the function to work properly?",
                max_mutations=10,
                mc_distractors=3,
            )
