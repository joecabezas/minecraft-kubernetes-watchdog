from os import environ

from dotenv import load_dotenv
from kubernetes import client
from kubernetes import config
load_dotenv(verbose=True)


class Cluster:

    KUBERNETES_SERVICE_HOST = environ.get('KUBERNETES_SERVICE_HOST')
    KUBERNETES_SERVICE_PORT = environ.get('KUBERNETES_SERVICE_PORT')

    TARGET_DEPLOYMENT_NAME = environ.get('TARGET_DEPLOYMENT_NAME')
    TARGET_NAMESPACE = environ.get('TARGET_NAMESPACE')

    def __init__(self):

        if (self.KUBERNETES_SERVICE_HOST and self.KUBERNETES_SERVICE_PORT):
            config.load_incluster_config()
        else:
            config.load_kube_config()

        self.api = client.AppsV1Api()

    def get_deployment_scale(self):
        return self.api.read_namespaced_deployment_scale(
            name=self.TARGET_DEPLOYMENT_NAME,
            namespace=self.TARGET_NAMESPACE,
        )

    def set_deployment_scale(self, replicas):

        scale = self.get_deployment_scale()
        scale.spec.replicas = replicas

        self.api.patch_namespaced_deployment_scale(
            self.TARGET_DEPLOYMENT_NAME,
            self.TARGET_NAMESPACE,
            body=scale,
        )
