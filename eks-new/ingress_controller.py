import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json
class IngressController_nginx_clb(pulumi.ComponentResource):
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
        self.nginx_ingress_clb = k8s.helm.v3.Release(f"{name}-nginx-ingress",
            chart="./charts/ingress-nginx",
            namespace="ingress-nginx-clb",
            #timeout=1800,
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
class IngressController_nginx_nlb(pulumi.ComponentResource):
    def __init__(self, name: str, cluster, opts: pulumi.ResourceOptions = None):
        super().__init__('custom:IngressController', name, None, opts)

        self.eip1 = aws.ec2.Eip("eip1", domain="vpc")
        self.eip2 = aws.ec2.Eip("eip2", domain="vpc")
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
        self.nginx_ingress_nlb = k8s.helm.v3.Release(f"{name}-nginx-ingress",
            chart="./charts/ingress-nginx",
            namespace="ingress-nginx-nlb",
            #timeout=1800,
            create_namespace=True,
            values={
                "controller": {
                    "service": {
                        "type": "LoadBalancer",
                        "annotations": pulumi.Output.all(cluster._name, self.ingress_sg.id, self.eip1.id, self.eip2.id).apply(
                            lambda args: {
                                #"service.beta.kubernetes.io/aws-load-balancer-name": f"{args[0]}-load-balancer",
                                "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                                "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type": "ip",
                                "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing",
                                "service.beta.kubernetes.io/aws-load-balancer-eip-allocations": f"{args[2]},{args[3]}",
                                "service.beta.kubernetes.io/aws-load-balancer-security-groups": args[1]
                            }
                        )
                    }
                }
            },
            opts=pulumi.ResourceOptions(provider=cluster.k8s_provider, parent=self)
        )

        self.register_outputs({})



class IngressController_aws_alb(pulumi.ComponentResource):
    def __init__(self, name: str, cluster, opts: pulumi.ResourceOptions = None):
        super().__init__('custom:IngressController', name, None, opts)
        # Create the Role for the ALB Ingress
        # alb_role = aws.iam.Role("alb-ingress-controller-role",
        #     assume_role_policy=json.dumps({
        #         "Version": "2012-10-17",
        #         "Statement": [{
        #             "Effect": "Allow",
        #             "Principal": {
        #                 "Federated": cluster.core.oidc_provider.arn
        #             },
        #             "Action": "sts:AssumeRoleWithWebIdentity",
        #             "Condition": {
        #                 "StringEquals": {
        #                     f"{cluster.core.oidc_provider.url}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller"
        #                 }
        #             }
        #         }]
        #     })
        # ) 

        # Attach necessary policies to the role (simplified for brevity)
        # aws.iam.RolePolicyAttachment("alb-ingress-controller-policy",
        #     policy_arn="arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess",
        #     role=alb_role.name
        # )



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

        # Deploy AWS Load Balancer Ingress Controller using local Helm chart
        self.aws_alb_ingress = k8s.helm.v3.Release(f"{name}-aws_alb_ingress",
            chart="./charts/aws-load-balancer-controller",
            namespace="kube-system",
            values={
                "clusterName": cluster._name,
#                "region": "us-west-2",  # Replace with your AWS region
#                "vpcId": self.vpc_id,  # Replace with your VPC ID
                "controller": {
                    "service": {
                        "type": "LoadBalancer",
                        "annotations": pulumi.Output.all(cluster._name, self.ingress_sg.id ).apply(
                            lambda args: {
#                                "eks.amazonaws.com/role-arn": alb_role.arn,
                                "alb.ingress.kubernetes.io/load-balancer-name": f"{args[0]}-load-balancer",
#                                "alb.ingress.kubernetes.io/subnets": args[2], 
#                                "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "tcp",
#                                "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
                                "alb.ingress.kubernetes.io/scheme": "internet-facing",
                                "alb.ingress.kubernetes.io/security-groups": args[1],
#                                "service.beta.kubernetes.io/aws-load-balancer-type": "external",
                                "alb.ingress.kubernetes.io/target-type": "ip"
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
