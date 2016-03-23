import os


def main():
    threads = int(os.getenv("THREADS", "1"))
    for i in range(1, threads):
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), str(i))
        for file in os.listdir(base_path):
            print os.path.join(base_path, file)


if __name__ == "__main__": main()
