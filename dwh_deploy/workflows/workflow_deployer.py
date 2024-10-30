import argparse
import glob
import importlib
import os
from hera.shared import global_config


class WorkFlowDeployer:
    """
    Класс для развертывания workflows в Argo WorkFlows
    """
    def __init__(self, env: str, app_name: str, flow_name: str):
        """
        :param env: окружение (проект) в которое развертываются флоу
        :param flow_name: имя флоу (может получить значение all, для развертывания всех флоу в проекте)
        :param app_name: имя приложения (поддиректория в workflow_apps)
        """
        self.env = env
        self.flow_name = flow_name
        self.app_name = app_name


    @property
    def workflow_files(self):
        current_directory = os.getcwd()
        flow_directory = os.path.join(current_directory, self.app_name, "workflows")
        file_paths = glob.glob(flow_directory + '/*.py')
        return [os.path.splitext(os.path.basename(file_path))[0]
                for file_path in file_paths] if self.flow_name == "all" else [self.flow_name + ".py"]


    def set_config(self, **kwargs):
        global_config.host = kwargs.get("host", os.environ.get("HOST"))
        global_config.token = kwargs.get("token", os.environ.get("TOKEN"))
        global_config.service_account_name = kwargs.get("service_account_name", os.environ.get("SERVICE_ACCOUNT_NAME"))
        global_config.namespace = kwargs.get("namespace", os.environ.get("NAMESPACE"))
        global_config.image = kwargs.get("image_path", os.environ.get("IMAGE_PATH"))


    def deploy_workflow(self, **kwargs):
        self.set_config(**kwargs)
        for file in self.workflow_files:
            module_workflow_name = os.path.splitext(file)[0]
            print(f"\nLaunching deploy workflows {module_workflow_name}!\n")
            importlib.import_module(f"workflows.{module_workflow_name}")
            print(f"\nDeploy workflows {module_workflow_name} for app {self.app_name} finished!\n")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Deploy Flow from specified files.")
    parser.add_argument("-wf", "--workflow_name", required=True, default="all", help="Name of the workflow to deploy")
    parser.add_argument("-app", "--app_name", required=True, help="Name of the app to deploy")
    parser.add_argument("-e", "--environment", required=True, help="Environment for deployment")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    deployer = WorkFlowDeployer(env=args.environment, flow_name=args.workflow_name, app_name=args.app_name)
    deployer.deploy_workflow()