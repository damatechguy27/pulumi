import pulumi
import pulumi_eks
import pulumi_kubernetes as k8s

def nginx_deploy(providers):
    ns = k8s.core.v1.Namespace("ns", pulumi.ResourceOptions(provider=providers))
    deployment = k8s.apps.v1.Deployment(
        "deploy",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            namespace= ns.metadata.name,
            labels={"app":"nginx"},
        ),
        spec=k8s.apps.v1.DeploymentSpecArgs(
            replicas=2,
            selector=k8s.meta.v1.LabelSelectorArgs(
                match_labels={"app":"nginx"},
            ),
        
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    labels={"app":"nginx"},
                ),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[
                        k8s.core.v1.ContainerArgs(
                            name="nginx",
                            image="nginx:latest",
                            ports=[k8s.core.v1.ContainerPortArgs(container_port=80)],
                        )
                    ],
                ),
            )
        ),    
    )
    # Export the name of the Deployment
    pulumi.export("deployment_name", deployment.metadata.name)
    