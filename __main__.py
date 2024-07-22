import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_awsx as awsx
import pulumi_kubernetes as k8s
#
#Creating ECR Repo
#


# Create an ECR repository
repo = aws.ecr.Repository('pulumi_ecr_repo')


# Create a Docker image
#docker_image = docker.Image("my-dockerimage",
#    build="./app", # Path to the directory containing your Dockerfile
#    image_name=repo.repository_url,
#    registry=aws.ecr.GetAuthorizationTokenArgs(registry_id=repo.registry_id))
#
#Creating kubernetes Cluster
#

# Create a VPC for the EKS cluster
vpc = aws.ec2.Vpc("pulum-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "pulum-vpc"})

# Create subnets for the EKS cluster
subnet1 = aws.ec2.Subnet("subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-west-2a")

subnet2 = aws.ec2.Subnet("subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-west-2b")

# Create an EKS cluster
cluster = eks.Cluster("pulum-cluster",
    vpc_id=vpc.id,
    subnet_ids=[subnet1.id, subnet2.id],
    instance_type="t3.micro",
    min_size=1,
    max_size=2,
    desired_capacity=1)

#
# EKS Cluster
#
# Deploy the Docker image to the EKS cluster
app_labels = {"app": "my-app"}

deployment = k8s.apps.v1.Deployment("my-deployment",
    spec={
        "selector": {"matchLabels": app_labels},
        "replicas": 2,
        "template": {
            "metadata": {"labels": app_labels},
            "spec": {
                "containers": [{
                    "name": "my-app",
                    "image": repo.repository_url.apply(lambda url: f"{url}:latest"),
                    "ports": [{"containerPort": 80}],
                }],
            },
        },
    })

# Create an EKS node group
node_group = eks.ManagedNodeGroup("pulum-nodegroup",
    cluster=cluster.core,
    node_group_name="pulum-nodegroup",
    node_role_arn=cluster.instance_role_arn,
    subnet_ids=cluster.subnet_ids,
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=1,
        max_size=2,
        min_size=1
    ),
    instance_types=["t3.micro"])


#
# Load Balancer 
#
# Create an Application Load Balancer
alb = aws.lb.LoadBalancer("my-alb",
    subnets=[subnet1.id, subnet2.id],
    security_groups=[cluster.cluster_security_group.id])

# Create a target group for the ALB
target_group = aws.lb.TargetGroup("my-target-group",
    vpc_id=vpc.id,
    port=80,
    protocol="HTTP",
    target_type="ip")

# Create a listener for the ALB
listener = aws.lb.Listener("my-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[{
        "type": "forward",
        "target_group_arn": target_group.arn
    }])


# Create a Kubernetes provider using the EKS cluster's kubeconfig
k8s_provider = k8s.Provider('k8s-provider', kubeconfig=cluster.kubeconfig)

# Export the repository URL & Export the cluster's kubeconfig
pulumi.export('repository_url', repo.repository_url)

pulumi.export("kubeconfig", cluster.kubeconfig)

# Export the ALB DNS name
pulumi.export("alb_dns_name", alb.dns_name)

# IAM Role
pulumi.export("instance_role", cluster.instance_role.arn)