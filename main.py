from file_parser import Parser

if __name__ == "__main__":
    files = Parser("replacement.py")
    for mut in files.all_mutations:
        print(repr(mut.replacement))
