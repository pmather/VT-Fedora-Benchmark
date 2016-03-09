from os import path, listdir


def main():
    base_path = path.join(path.dirname(path.dirname(path.realpath(__file__))), "experiments")
    for file in listdir(base_path):
        print path.join(base_path, file)


if __name__ == "__main__": main()
