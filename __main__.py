import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
#
#Creating ECR Repo
#


# Create an ECR repository
repo = aws.ecr.Repository('pulumi_ecr_repo')

#
#Creating kubernetes Cluster
#

# Create a VPC for our cluster
vpc = aws.ec2.Vpc("pulumi-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True)

# Create public subnets
public_subnet_a = aws.ec2.Subnet("public-subnet-a",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-west-2a",
    map_public_ip_on_launch=True)

public_subnet_b = aws.ec2.Subnet("public-subnet-b",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-west-2b",
    map_public_ip_on_launch=True)

# Create an EKS cluster
cluster = eks.Cluster("pulum-cluster",
    vpc_id=vpc.id,
    public_subnet_ids=[public_subnet_a.id, public_subnet_b.id],
    instance_type="t3.micro",
    desired_capacity=2,
    min_size=1,
    max_size=3)

# Create a node group
node_group = eks.NodeGroup("pulum-node",
    cluster=cluster.core,
    instance_type="t3.micro",
    desired_capacity=2,
    min_size=1,
    max_size=3,
    labels={"role": "general"},
    taints=[{"key": "workload", "value": "general", "effect": "NO_SCHEDULE"}])

# EKS Deployment
app_labels = { 'app': 'my-app' }
deployment = k8s.apps.v1.Deployment('my-app-deployment',
    spec={
        'selector': { 'match_labels': app_labels },
        'replicas': 1,
        'template': {
            'metadata': { 'labels': app_labels },
            'spec': {
                'containers': [{
                    'name': 'my-app',
                    'image': repo.repository_url.apply(lambda url: f"{url}:latest"),
                    'ports': [{ 'container_port': 80 }]
                }]
            }
        }
    },
    opts=pulumi.ResourceOptions(provider=k8s.Provider('k8s-provider', kubeconfig=cluster.kubeconfig))
)


# EKS Deployment Service 
service = k8s.core.v1.Service('my-app-service',
    spec={
        'selector': app_labels,
        'ports': [{ 'port': 80, 'target_port': 80 }],
        'type': 'LoadBalancer'
    },
    opts=pulumi.ResourceOptions(provider=k8s.Provider('k8s-provider', kubeconfig=cluster.kubeconfig))
)


# Export the repository URL & Export the cluster's kubeconfig
pulumi.export('repository_url', repo.repository_url)

pulumi.export("kubeconfig", cluster.kubeconfig)
