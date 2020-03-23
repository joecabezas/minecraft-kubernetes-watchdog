import logging
from os import environ

from environs import Env
from kubernetes import client
from kubernetes import config

env = Env()
env.read_env()

KUBERNETES_SERVICE_HOST = env('KUBERNETES_SERVICE_HOST', None)
KUBERNETES_SERVICE_PORT = env('KUBERNETES_SERVICE_PORT', None)

TARGET_DEPLOYMENT_NAME = env('TARGET_DEPLOYMENT_NAME')
TARGET_NAMESPACE = env('TARGET_NAMESPACE')


class Cluster:
    def __init__(self):
        logging.info("Target deployment name: %s", TARGET_DEPLOYMENT_NAME)
        logging.info("Target namespace: %s", TARGET_NAMESPACE)

        if (KUBERNETES_SERVICE_HOST and KUBERNETES_SERVICE_PORT):
            logging.info("Using in-cluster config")
            config.load_incluster_config()
        else:
            logging.info("Using kube config file")
            config.load_kube_config()

        self.api = client.AppsV1Api()

    def get_deployment_scale(self):
        return self.api.read_namespaced_deployment_scale(
            name=TARGET_DEPLOYMENT_NAME,
            namespace=TARGET_NAMESPACE,
        )

    def get_deployment_status(self):
        return self.api.read_namespaced_deployment_status(
            name=TARGET_DEPLOYMENT_NAME,
            namespace=TARGET_NAMESPACE,
        )

    def set_deployment_scale(self, replicas):
        scale = self.get_deployment_scale()
        scale.spec.replicas = replicas

        self.api.patch_namespaced_deployment_scale(
            TARGET_DEPLOYMENT_NAME,
            TARGET_NAMESPACE,
            body=scale,
        )
