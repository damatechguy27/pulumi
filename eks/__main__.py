import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json
from eks import newcluster
cluster1 = newcluster("cluster1")

# Export the cluster IAM role, node instance roles, and node group
pulumi.export("Cluster Role", cluster1.cluster_iam_role)
pulumi.export("Node Roles", cluster1.instance_roles)
pulumi.export("Node Group", cluster1.node_group)