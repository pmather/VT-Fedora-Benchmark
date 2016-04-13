import orchestrator
import os
import sys
import uuid
from subprocess import Popen


class RktManager(orchestrator.WorkerManager):
    def __init__(self, host_uid, rabbitmq_host, rabbitmq_username, rabbitmq_password, volume):
        super(RktManager, self).__init__(host_uid, rabbitmq_host, rabbitmq_username, rabbitmq_password)
        self.result_directories = open(orchestrator.WorkerManager.RUNNING_WORKERS_FILENAME, "w+")
        self.project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.volume = volume
        self.opened_processes = []

    @staticmethod
    def fetch_results():
        with open(orchestrator.WorkerManager.RUNNING_WORKERS_FILENAME) as f:
            result_directories = f.readlines()
        for base_path in result_directories:
            base_path = base_path.strip()
            if os.path.exists(base_path):
                for file in os.listdir(base_path):
                    print os.path.join(base_path, file)

    def start_workers(self, count, control_topic_name, work_queue_name, acknowledge_queue, correlation_id):
        for i in range(1, count + 1):
            id = self.host_uid + "_" + str(i)
            base_path = os.path.join(self.project_dir, str(i))
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            with open(os.path.join(base_path, "experiment.out"), "w") as f, open(os.devnull, 'w') as fnull:
                self.opened_processes.append(
                    Popen(["sudo", "rkt", "run", "--insecure-options=image", "--volume", "results,kind=host,source=" + base_path + ",readOnly=false",
                           "docker://dedocibula/fedora-benchmark", "--mount",
                           "volume=results,target=" + self.volume,
                           "--exec", "python", "--", "experiment_coordinator.py",
                           self.rabbitmq_host, self.rabbitmq_username,
                           self.rabbitmq_password, id, control_topic_name, work_queue_name, acknowledge_queue,
                           correlation_id, self.volume],
                          cwd=base_path, stdout=f, stderr=fnull))
            self.result_directories.write(base_path + "\n")
        self.result_directories.flush()

    def stop_workers(self):
        for proc in self.opened_processes:
            proc.wait()
        self.opened_processes = []
        self.result_directories.seek(0)
        self.result_directories.truncate()


def main():
    command = sys.argv[1]

    if command == "start_with":
        orchestrator.start_with(RktManager(str(uuid.uuid4()), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    elif command == "fetch_results":
        RktManager.fetch_results()
    else:
        print "Unrecognized command"


if __name__ == '__main__': main()
