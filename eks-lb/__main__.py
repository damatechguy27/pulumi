import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json
from os.path import join
from eks import newcluster
from app_deployments import nginx_deploy
#import nginx





#creating cluster here 
cluster1 = newcluster(
    "cluster1"
)



#nginx_deploy(cluster1.cluster_provider)

# Export the cluster IAM role, node instance roles, and node group
pulumi.export("Cluster Role", cluster1.cluster_iam_role)
pulumi.export("Node Roles", cluster1.instance_roles)
#pulumi.export("Node Group", cluster1.node_group)
pulumi.export("provider", cluster1.k8s_provider)


# Create a Kubernetes provider using the EKS cluster's kubeconfig
# k8s_provider = k8s.Provider("k8s-provider",
#     kubeconfig=cluster1.cluster_kubeconfig
# )

# Deploy NGINX Ingress Controller using local Helm chart
nginx_ingress = k8s.helm.v3.Release("nginx-ingress",
    chart="./charts/ingress-nginx",  # Path to your local chart
    namespace="ingress-nginx",
    create_namespace=True,
    values={
        "controller": {
            "service": {
                "type": "LoadBalancer",
                "externalTrafficPolicy": "Local"
            },
            "config": {
                "use-forwarded-headers": "true"
            },
            "metrics": {
                "enabled": "true"
            }
        }
    },
    opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider)
)

# Export the Load Balancer hostname
ingress_service = k8s.core.v1.Service.get(
    "ingress-nginx-controller-service",
    f"{nginx_ingress.namespace}/ingress-nginx-controller",    
    opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider, depends_on=[nginx_ingress])
)

#pulumi.export("load_balancer_hostname", ingress_service.status.apply(lambda s: s.load_balancer.ingress[0].hostname))
pulumi.export("load_balancer_hostname", ingress_service.status.load_balancer.ingress[0].hostname)




# # Define the namespace where the NGINX Ingress Controller will be deployed
# namespace = k8s.core.v1.Namespace("nginx-ingress",
#                                   metadata=k8s.meta.v1.ObjectMetaArgs(
#                                       name="nginx-ingress"
#                                   ))

# # Create a Security Group to allow HTTP and HTTPS traffic
# security_group = aws.ec2.SecurityGroup("security-group",
#     #vpc_id=vpc.id,
#     description="Enable HTTP and HTTPS access",
#     ingress=[
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol="tcp",
#             from_port=80,
#             to_port=80,
#             cidr_blocks=["0.0.0.0/0"]
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol="tcp",
#             from_port=443,
#             to_port=443,
#             cidr_blocks=["0.0.0.0/0"]
#         )
#     ],
#     egress=[
#         aws.ec2.SecurityGroupEgressArgs(
#             protocol="-1",
#             from_port=0,
#             to_port=0,
#             cidr_blocks=["0.0.0.0/0"]
#         )
#     ])

# # Deploy the NGINX Ingress Controller using a local Helm chart
# nginx_ingress = k8s.helm.v4.Chart("nginx-ingress",
#                                         chart="./charts/ingress-nginx",
#                                         namespace=namespace.metadata.name,
#                                         values={
#                                         "controller": {
#                                             "service": {
#                                                 "type": "LoadBalancer",
#                                                 "annotations": {
#                                                     "service.beta.kubernetes.io/aws-load-balancer-security-groups": security_group.id
#                                                 }
#                                             }
#                                         }
#                                     }
#                                 )

# # Export the DNS name of the LoadBalancer
# ingress_service = nginx_ingress.get_resource("v1/Service", "nginx-ingress-controller")
# pulumi.export("loadBalancerDNS", ingress_service.status["loadBalancer"]["ingress"][0]["hostname"])