from mutation_generator import MutatedFiles

if __name__ == "__main__":
    files = MutatedFiles("replacement.py")
    for mut in files.all_mutations:
        print(repr(mut.replacement))
