import os
from subprocess import call


def main():
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "experiments")
    for file in os.listdir(base_path):
        file_path = os.path.join(base_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e
    call("docker cp fedora_benchmark:/vt-fedora-benchmark/experiments/. {}".format(base_path), shell=True)
    with open(os.path.join(base_path, "experiment.out"), "w") as f, open(os.devnull, 'w') as fnull:
        call(["docker", "logs", "fedora_benchmark"], stdout=f, stderr=fnull)
    for file in os.listdir(base_path):
        print os.path.join(base_path, file)


if __name__ == "__main__": main()
