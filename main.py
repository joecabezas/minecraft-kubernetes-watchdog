from os import environ

from pprint import pprint
from kubernetes import client, config

KUBERNETES_SERVICE_HOST = "KUBERNETES_SERVICE_HOST"
KUBERNETES_SERVICE_PORT = "KUBERNETES_SERVICE_PORT"

def main():
    if (KUBERNETES_SERVICE_HOST in environ and
            KUBERNETES_SERVICE_PORT in environ):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    api_instance = client.AppsV1Api()

    # Uncomment the following lines to enable debug logging
    # c = client.Configuration()
    # c.debug = True
    # api_instance = client.AppsV1Api(api_client=client.ApiClient(configuration=c))

    name = 'mc-minecraft' # str | name of the Scale
    namespace = 'default' # str | object name and auth scope, such as for teams and projects
    pretty = True # str | If 'true', then the output is pretty printed. (optional)
    field_manager = 'field_manager_example' # str | fieldManager is a name associated with the actor or entity that is making these changes. The value must be less than or 128 characters long, and only contain printable characters, as defined by https://golang.org/pkg/unicode/#IsPrint. This field is required for apply requests (application/apply-patch) but optional for non-apply patch types (JsonPatch, MergePatch, StrategicMergePatch). (optional)

    scale = api_instance.read_namespaced_deployment_scale(
        name=name,
        namespace=namespace,
        pretty=pretty
    )
    pprint(scale)

    scale.spec.replicas = 0

    api_response = api_instance.patch_namespaced_deployment_scale(
        name,
        namespace,
        body=scale,
        pretty=pretty,
        # dry_run=dry_run,
        field_manager=field_manager,
    )
    pprint(api_response)

if __name__ == '__main__':
    main()
