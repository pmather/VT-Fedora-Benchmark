from os import path, listdir, devnull
from subprocess import call


def main():
    base_path = path.join(path.dirname(path.dirname(path.realpath(__file__))), "experiments")
    call("docker cp fedora_benchmark:/vt-fedora-benchmark/experiments/. {}".format(base_path), shell=True)
    with open(path.join(base_path, "experiment.out"), "w") as f, open(devnull, 'w') as fnull:
        call(["docker", "logs", "fedora_benchmark"], stdout=f, stderr=fnull)
    for file in listdir(base_path):
        print path.join(base_path, file)


if __name__ == "__main__": main()
