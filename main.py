from file_parser import Meta

if __name__ == "__main__":
    files = Meta("file_parser.py")
    for tup in files.all_mutations:
        print(repr(tup[2]))
