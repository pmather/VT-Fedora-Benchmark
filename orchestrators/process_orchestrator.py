import orchestrator
import os
import sys
import uuid
import shutil
from subprocess import Popen


class ProcessManager(orchestrator.WorkerManager):
    RESULT_DIRS_FILENAME = "running-containers.txt"

    def __init__(self, host_uid, rabbitmq_host, rabbitmq_username, rabbitmq_password):
        super(ProcessManager, self).__init__(host_uid, rabbitmq_host, rabbitmq_username, rabbitmq_password)
        self.result_directories = open(ProcessManager.RESULT_DIRS_FILENAME, "wr+")
        self.project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    @staticmethod
    def fetch_results():
        with open(ProcessManager.RESULT_DIRS_FILENAME) as f:
            result_directories = f.readlines()
        for base_path in result_directories:
            for file in os.listdir(base_path):
                print os.path.join(base_path, file)

    def start_workers(self, count, control_topic_name, work_queue_name):
        for i in range(1, count + 1):
            base_path = os.path.join(self.project_dir, str(i + 1))
            if not os.path.exists(base_path):
                os.makedirs(base_path)
                shutil.copytree(os.path.join(self.project_dir, "experiments"), base_path)
            command = os.path.join(base_path, "experiment_coordinator.py")
            output = os.path.join(base_path, "experiment.out")
            Popen(["python", command, self.rabbitmq_host, self.rabbitmq_username, self.rabbitmq_host,
                   self.host_uid + "_" + str(i), self.host_uid, str(id), control_topic_name, work_queue_name, ">",
                   output])
            self.result_directories.write(base_path + "\n")

    def stop_workers(self):
        self.result_directories.seek(0)
        self.result_directories.truncate()


def main():
    command = sys.argv[1]

    if command == "start_with":
        orchestrator.start_with(ProcessManager(uuid.uuid4(), sys.argv[2], sys.argv[3], sys.argv[4]))
    elif command == "fetch_results":
        ProcessManager.fetch_results()
    else:
        print "Unrecognized command"


if __name__ == '__main__': main()
