from os import path, listdir
from subprocess import call


def main():
    base_path = path.join(path.dirname(path.dirname(path.realpath(__file__))), "experiments")
    call("docker cp fedora_benchmark:/vt-fedora-benchmark/experiments/. {}".format(base_path), shell=True)
    call("docker logs fedora_benchmark > {}/experiment.out".format(base_path), shell=True)
    for file in listdir(base_path):
        print path.join(base_path, file)


if __name__ == "__main__": main()
