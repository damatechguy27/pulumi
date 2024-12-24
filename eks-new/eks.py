import pulumi
from pulumi import ResourceOptions
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json
from eks_addons import eks_Addons
from eks_iam_roles import eks_addon_policy, eks_lb_policy
import os
#from pulumi_resources.k8s import ServiceAccountRole

# Example
# https://github.com/sublee/pulumi-eks/blob/75a6804fbc67dd7a5662664c6063a4c44d69b5ec/examples/nodegroup-py/__main__.py#L66
# https://www.youtube.com/watch?v=gxLyAr0lUg0
# https://github.com/pulumi/templates/blob/master/kubernetes-aws-python/__main__.py
# https://github.com/pulumi/templates/blob/master/helm-kubernetes-python/__main__.py
# https://github.com/pulumi/templates/blob/master/webapp-kubernetes-python/__main__.py
#

config = pulumi.Config("infra")
enable_delete_before_update = config.get_bool("delete_before_replace")
class newcluster(pulumi.ComponentResource):
    def __init__(self, name:str):
        super().__init__('custom:resource:newcluster', name)
        

        #setting up principal IAM role if you are using config maps
        # Create an IAM role, this is role you will be assuming 





        self.cluster = eks.Cluster(
            name,
            #desired_capacity=1,
            #min_size= 1,
            #max_size= 2,
            skip_default_node_group=True,
            endpoint_public_access=True,
            endpoint_private_access=True,
            version="1.31",
            create_oidc_provider=True
            #authentication_mode= eks.AuthenticationMode.API_AND_CONFIG_MAP
        )

        # Store the IAM role and instance roles as output properties
        self.cluster_iam_role = self.cluster.instance_roles.apply(lambda roles: roles[0].arn)
        self.instance_roles = self.cluster.instance_roles
        #self.cluster_provider= self.cluster._provider
        self.cluster_kubeconfig = self.cluster.kubeconfig

        

        # Configure the Kubernetes provider for cluster to assume cluster role created above
        self.k8s_provider = k8s.Provider("k8s-provider", kubeconfig=self.cluster_kubeconfig)

        admin_cluster_role = k8s.rbac.v1.ClusterRole(
            f"{name}-cluster_role",
            rules=[
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=["*"], resources=["*"], verbs=["*"]
                )
            ],
            opts=ResourceOptions(provider=self.k8s_provider)
        )

        k8s.rbac.v1.ClusterRoleBinding(
            f"{name}-admin-role-binding",
            role_ref=k8s.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=admin_cluster_role.metadata.name
            ),
            opts=ResourceOptions(provider=self.k8s_provider)
        )

# managed Node group automatically makes the EBS root volume a GP3 
# automatically deploys nodes within a launch template
# and adds the role of the cluster, But does not automatically add the tags with hash
        # self.node_group = eks.ManagedNodeGroup(
        #     f"{name}-node-group",
        #     cluster=self.cluster,
        #     node_role=self.instance_roles[0],
        #     instance_types=["t3.medium"],
        #     scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        #         desired_size=1,
        #         min_size=1,
        #         max_size=2,
        #     ),
        #     #instance_profile=instance_profile_arn,
        #     opts=pulumi.ResourceOptions(parent=self)
        # )


# Create a Node Group using the service role and instance roles from the cluster
# This Profile is passed into the V2 module to 
        self.instance_profile_name = aws.iam.InstanceProfile(
            f"{name}-instance-profile",
            role=self.instance_roles[0].name
        )

# NodeGroupV2 deploy launch template automatically 
# uses a cluster profile to add roles to the eks nodes
        self.node_group3 = eks.NodeGroupV2(
            f"{name}-node-groupV2",
            cluster=self.cluster,
            instance_profile=self.instance_profile_name,
            instance_type="t3.medium",
            desired_capacity=2,
            min_size=2,
            max_size=4,
            #encrypt_root_block_device=True,
            node_root_volume_encrypted=True,
            node_root_volume_size=50,
            node_root_volume_type='gp3',
            launch_template_tag_specifications=[{
                "resourceType":"instance",
                "tags":{
                    "Environment":"Dev",
                    "Purpose":"EKSNode"
                }
                
            }],
            opts=pulumi.ResourceOptions(parent=self)
        )


        # self.register_outputs({
        #     "cluster_iam_role": self.cluster_iam_role,
        #     "instance_roles": self.instance_roles
        # })



        oidc_arn = self.cluster.core.oidc_provider.arn
        oidc_url = self.cluster.core.oidc_provider.url        

        # Create an roles with federate policy for service account to assume
        # EKS add ons
        
        # Create a namespace
        self.eks_addon_namespace = k8s.core.v1.Namespace("addon-namespace",
            metadata={"name": "addon-namespace"},
            opts=pulumi.ResourceOptions(provider=self.k8s_provider)
        )

        self.eks_addon_sa_assume_role = aws.iam.Role("eks-addon-sa-role",
            assume_role_policy=pulumi.Output.all(self.cluster.core.oidc_provider.url, self.cluster.core.oidc_provider.arn).apply(
                lambda args: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": args[1]
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                f"{args[0]}:sub": f"system:serviceaccount:{self.eks_addon_namespace.metadata['name']}:addon-manager-sa"
                            }
                        }
                    }]
                })
            )
        )


        # Attach the add-on management policy to the IAM role
        aws.iam.RolePolicyAttachment("eks-addon-policy-attachment1",
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEFSCSIDriverPolicy",
            role=self.eks_addon_sa_assume_role.name
        )

        aws.iam.RolePolicyAttachment("eks-addon-policy-attachment2",
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy",
            role=self.eks_addon_sa_assume_role.name
        )


        # Create eks add on service account
        self.eks_addon_service_account = k8s.core.v1.ServiceAccount("eks-addon-sa",
            metadata={
                "name": "eks-addon-sa",
                "namespace": self.eks_addon_namespace.metadata["name"],
                "annotations": {
                    "eks.amazonaws.com/role-arn": self.eks_addon_sa_assume_role.arn
                }
            },
            opts=pulumi.ResourceOptions(provider=self.k8s_provider)
        )


        # adding EKS add on
        self.addon_efs = eks_Addons("EFS-CSI-driver","aws-efs-csi-driver", self.cluster,"v2.1.0-eksbuild.1", self.eks_addon_sa_assume_role.arn)
        self.addon_ebs = eks_Addons("EBS-CSI-driver","aws-ebs-csi-driver" ,self.cluster,"v1.37.0-eksbuild.1", self.eks_addon_sa_assume_role.arn)


        # Load balancer controller
        self.eks_elb_sa_assume_role = aws.iam.Role("aws-load-balancer-controller",
            assume_role_policy=pulumi.Output.all(self.cluster.core.oidc_provider.url, self.cluster.core.oidc_provider.arn).apply(
                lambda args: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": args[1]
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                f"{args[0]}:sub": f"system:serviceaccount:kube-system:aws-load-balancer-controller"
                            }
                        }
                    }]
                })
            )
        )

        aws.iam.RolePolicyAttachment("eks-elb-policy-attachment",
            policy_arn=eks_lb_policy.arn,
            role=self.eks_elb_sa_assume_role.name
        )

        aws.iam.RolePolicyAttachment("eks-elb-policy-attachment2",
            policy_arn="arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess",
            role=self.eks_elb_sa_assume_role.name
        )

        # Deploy AWS Load Balancer Controller using Helm
        lb_controller = k8s.helm.v3.Release("aws-load-balancer-controller",
            chart="aws-load-balancer-controller",
            namespace="kube-system",
            repository_opts=k8s.helm.v3.RepositoryOptsArgs(
                repo="https://aws.github.io/eks-charts"
            ),
            values={
                "clusterName": self.cluster.name,
                "serviceAccount": {
                    "create": True,
                    "name": "aws-load-balancer-controller",
                    "annotations": {
                        "eks.amazonaws.com/role-arn": self.eks_elb_sa_assume_role.arn
                    }
                },
                "region": "us-west-2",  # Replace with your desired region
                "vpcId": self.cluster.vpc_id
            },
            opts=pulumi.ResourceOptions(provider=self.k8s_provider)
        )

        # Create a Kubernetes service with NLB annotations
        nlb_service = k8s.core.v1.Service("my-nlb-service",
            metadata={
                "name": "my-nlb-service",
                "annotations": {
                    "service.beta.kubernetes.io/aws-load-balancer-type": "external",
                    "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type": "ip",
                    "service.beta.kubernetes.io/aws-load-balancer-scheme": "internet-facing"
                }
            },
            spec={
                "type": "LoadBalancer",
                "ports": [{
                    "port": 80,
                    "targetPort": 8080
                }],
                "selector": {
                    "app": "my-app"
                }
            },
            opts=pulumi.ResourceOptions(provider=self.k8s_provider)
        )



        self.register_outputs({
            "cluster_iam_role": self.cluster_iam_role,
            "instance_roles": self.instance_roles,
            "kubeconfig": self.cluster_kubeconfig
            #"node_group": self.node_group,
        })