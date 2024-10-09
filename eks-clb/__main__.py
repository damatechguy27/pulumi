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

# Create a security group for the ingress load balancer
ingress_sg = aws.ec2.SecurityGroup("ingress-sg",
    description="Security group for ingress-nginx load balancer",
    #vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["192.168.1.22/32"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)

# # Deploy NGINX Ingress Controller using local Helm chart
# nginx_ingress = k8s.helm.v3.Release("nginx-ingress",
#     chart="./charts/ingress-nginx",
#     namespace="ingress-nginx",
#     create_namespace=True,
#     values={
#         "controller": {
#             "service": {
#                 "type": "LoadBalancer",
#                 "annotations": pulumi.Output.all(cluster1._name, ingress_sg.id).apply(
#                     lambda args: {
#                         "service.beta.kubernetes.io/aws-load-balancer-name": f"{args[0]}-load-balancer",
#                         "service.beta.kubernetes.io/aws-load-balancer-type": "external",
#                         "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
#                         "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
#                         "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing",
#                         "service.beta.kubernetes.io/aws-load-balancer-security-groups": args[1]
#                     }
#                 )
#             }
#         }
#     },
#     opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider)
# )

# Deploy NGINX Ingress Controller using local Helm chart
nginx_ingress = k8s.helm.v3.Release("nginx-ingress",
    chart="./charts/ingress-nginx",
    namespace="ingress-nginx",
    create_namespace=True,
    values={
        "controller": {
            "service": {
                "type": "LoadBalancer",
                "annotations": {
                    "service.beta.kubernetes.io/aws-load-balancer-name": f"{cluster1._name}-load-balancer",
                    #"service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                    #"service.beta.kubernetes.io/aws-load-balancer-internal": "false",
                    #"service.beta.kubernetes.io/aws-load-balancer-nlb-target-type": "instance",
                    "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
                    "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
                    "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing",
                    #"service.beta.kubernetes.io/aws-load-balancer-manage-backend-security-group-rules": "true",
                    # This annotation is crucial for attaching a security group
                    "service.beta.kubernetes.io/aws-load-balancer-security-groups": ingress_sg.id
                }
            }
        }
    },
    opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider)
)