import pulumi
import pulumi_aws as aws
import json
from pulumi_aws import iam
#############################################
# IAM Role for EKS Cluster
cluster_role = aws.iam.Role("clusterRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "eks.amazonaws.com"},
            "Effect": "Allow",
            "Sid": ""
        }]
    })
)

# Attach policies to the Cluster role
cluster_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController",
    "arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
    ]


for cluster_policy_arn in cluster_policy_arns:
    aws.iam.RolePolicyAttachment(f"{cluster_role._name}-{cluster_policy_arn.split('/')[-1]}",
                                role=cluster_role.name,
                                policy_arn=cluster_policy_arn)


cluster_profile = aws.iam.InstanceProfile("clusterProfile", role=cluster_role.name)

# IAM Role for EKS Node Group
node_group_role = aws.iam.Role("nodeGroupRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Effect": "Allow",
            "Sid": ""
        }]
    })
)


# Attach policies to the Node Group role
policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
]
for policy_arn in policy_arns:
    aws.iam.RolePolicyAttachment(f"{node_group_role._name}-{policy_arn.split('/')[-1]}",
                                role=node_group_role.name,
                                policy_arn=policy_arn)

# Instance profile for the node group
nodegroup_profile = aws.iam.InstanceProfile("nodegroupProfile", role=node_group_role.name)

pulumi.export("ClusterProfileName", cluster_profile.name)
pulumi.export("instanceProfileName", nodegroup_profile.name)