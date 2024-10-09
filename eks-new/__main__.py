import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json
from os.path import join
from eks import newcluster
from ingress_controller import IngressController
#import nginx





#creating cluster here 
cluster1 = newcluster(
    "cluster1"
)

nginx = IngressController("ingress",cluster1)



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

