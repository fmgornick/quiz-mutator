class QuizMeta:
    def __init__(
        self,
        quiz_title: str = "problem bank",
        zip_filename: str = "problem_bank",
        reorder_prompt: str = "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now.",
        find_mutation_prompt: str = "which line contains the mutation?",
        classify_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        fix_mutation_prompt: str = "what change needs to be made for the function to work properly?",
        max_mutations: int = 10,
        mc_distractors: int = 3,
    ):
        self.quiz_title = quiz_title
        self.zip_filename = zip_filename
        self.reorder_prompt = reorder_prompt
        self.find_mutation_prompt = find_mutation_prompt
        self.classify_mutation_prompt = classify_mutation_prompt
        self.fix_mutation_prompt = fix_mutation_prompt
        self.max_mutations = max_mutations
        self.mc_distractors = mc_distractors


def customize_quiz() -> QuizMeta:
    yn = input("do you want to customize your zip file? (y/n): ")
    if yn != "y":
        return QuizMeta()
    else:
        print("\nfor any of the following prompts, just hit enter for default...")
        quiz_title = input('quiz title (default = "problem bank"): ') or "problem bank"

        zip_filename = (
            input('zip filename (default = "problem_bank"): ').replace(" ", "_")
            or "problem_bank"
        )

        reorder_prompt = (
            input("reorder prompt: ")
            or "correct the order of these lines.  one line contains an incorrect mutation, ignore it for now."
        )

        find_mutation_prompt = (
            input("find mutation prompt: ") or "which line contains the mutation?"
        )

        classify_mutation_prompt = (
            input("classify mutation prompt: ")
            or "what change needs to be made for the function to work properly?"
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
            zip_filename=zip_filename,
            reorder_prompt=reorder_prompt,
            find_mutation_prompt=find_mutation_prompt,
            classify_mutation_prompt=classify_mutation_prompt,
            fix_mutation_prompt=fix_mutation_prompt,
            max_mutations=max_mutations,
            mc_distractors=mc_distractors,
        )
