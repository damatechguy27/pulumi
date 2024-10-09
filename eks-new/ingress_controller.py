import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s

class IngressController(pulumi.ComponentResource):
    def __init__(self, name: str, cluster, opts: pulumi.ResourceOptions = None):
        super().__init__('custom:IngressController', name, None, opts)

        # Create a security group for the ingress load balancer
        self.ingress_sg = aws.ec2.SecurityGroup(f"{name}-ingress-sg",
            description="Security group for ingress-nginx load balancer",
            #vpc_id=vpc_id,
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
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Deploy NGINX Ingress Controller using local Helm chart
        self.nginx_ingress = k8s.helm.v3.Release(f"{name}-nginx-ingress",
            chart="./charts/ingress-nginx",
            namespace="ingress-nginx",
            create_namespace=True,
            values={
                "controller": {
                    "service": {
                        "type": "LoadBalancer",
                        "annotations": pulumi.Output.all(cluster._name, self.ingress_sg.id).apply(
                            lambda args: {
                                "service.beta.kubernetes.io/aws-load-balancer-name": f"{args[0]}-load-balancer",
                                "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
                                "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
                                "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing",
                                "service.beta.kubernetes.io/aws-load-balancer-security-groups": args[1]
                            }
                        )
                    }
                }
            },
            opts=pulumi.ResourceOptions(provider=cluster.k8s_provider, parent=self)
        )

        self.register_outputs({})

    # def get_ingress_service(self):
    #     return k8s.core.v1.Service.get(
    #         "ingress-nginx-controller-service",
    #         f"{self.nginx_ingress.namespace}/ingress-nginx-controller",    
    #         opts=pulumi.ResourceOptions(parent=self)
    #     )
