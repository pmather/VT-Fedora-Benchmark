import os
from subprocess import call


def main():
    threads = int(os.getenv("THREADS", "1"))
    for i in range(1, threads + 1):
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), str(i))
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        for file in os.listdir(base_path):
            file_path = os.path.join(base_path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        call("docker cp fedora_benchmark_{}:/vt-fedora-benchmark/experiments/. {}".format(str(i), base_path), shell=True)
        with open(os.path.join(base_path, "experiment.out"), "w") as f, open(os.devnull, 'w') as fnull:
            call(["docker", "logs", "fedora_benchmark_{}".format(str(i))], stdout=f, stderr=fnull)
        for file in os.listdir(base_path):
            print os.path.join(base_path, file)


if __name__ == "__main__": main()
