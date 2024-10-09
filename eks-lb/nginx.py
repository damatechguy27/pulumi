import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs
import pulumi_aws as aws

# Initialize the Kubernetes provider (Make sure kubeconfig is properly set up in your environment)
k8s_provider = k8s.Provider("k8s-provider")

# Deploy the NGINX Ingress controller using the Helm chart
nginx_ingress = Release(
    "nginx-ingress",
    ReleaseArgs(
        chart="nginx-ingress",
        version="1.41.3",  # Specify the version of the chart (adjust as necessary)
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://kubernetes.github.io/ingress-nginx"
        ),
        values={
            "controller": {
                "service": {
                    "type": "LoadBalancer"
                }
            }
        },
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Create a sample Backend Service (Assume the deployment is already there)
backend_service = k8s.core.v1.Service.get(
    "backend-service",
    "default/backend-service-name",
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Create an Ingress resource to route traffic
ingress = k8s.networking.v1.Ingress(
    "example-ingress",
    metadata={
        "name": "example-ingress",
        "annotations": {
            "nginx.ingress.kubernetes.io/rewrite-target": "/",
        },
    },
    spec={
        "rules": [{
            "http": {
                "paths": [{
                    "path": "/",
                    "pathType": "Prefix",
                    "backend": {
                        "service": {
                            "name": backend_service.metadata.name,
                            "port": {
                                "number": 80
                            }
                        }
                    }
                }]
            }
        }]
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Extract the LoadBalancer information
ingress_service = nginx_ingress.status.apply(lambda status: status["deployedResources"]["Service"]["nginx-ingress-controller"])

# Get the LoadBalancer security group
lb_sg_id = ingress_service.apply(lambda svc: svc.status.load_balancer.ingress[0].hostname if svc.status.load_balancer.ingress[0].hostname else svc.status.load_balancer.ingress[0].ip)

# Allow incoming traffic on port 80 and 443 for the load balancer
security_group_rule_80 = aws.ec2.SecurityGroupRule(
    "allow-http",
    type="ingress",
    from_port=80,
    to_port=80,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lb_sg_id,
)

security_group_rule_443 = aws.ec2.SecurityGroupRule(
    "allow-https",
    type="ingress",
    from_port=443,
    to_port=443,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=lb_sg_id,
)

# Export the LoadBalancer IP or hostname
pulumi.export("nginx_lb_ip_or_hostname", ingress_service)
