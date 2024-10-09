import pulumi
from pulumi import ResourceOptions
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json

# Example
# https://github.com/sublee/pulumi-eks/blob/75a6804fbc67dd7a5662664c6063a4c44d69b5ec/examples/nodegroup-py/__main__.py#L66
# https://www.youtube.com/watch?v=gxLyAr0lUg0
# https://github.com/pulumi/templates/blob/master/kubernetes-aws-python/__main__.py
# https://github.com/pulumi/templates/blob/master/helm-kubernetes-python/__main__.py
# https://github.com/pulumi/templates/blob/master/webapp-kubernetes-python/__main__.py
#
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



        # Create a Node Group using the service role and instance roles from the cluster
        # This Profile is passed into the V2 module to 
        self.instance_profile_name = aws.iam.InstanceProfile(
            f"{name}-instance-profile",
            role=self.instance_roles[0].name
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

# NodeGroupV2 deploy launch template automatically 
# uses a cluster profile to add roles to the eks nodes

        self.node_group3 = eks.NodeGroupV2(
            f"{name}-node-groupV2",
            cluster=self.cluster,
            instance_profile=self.instance_profile_name,
            instance_type="t3.medium",
            desired_capacity=1,
            min_size=1,
            max_size=2,
            #encrypt_root_block_device=True,
            node_root_volume_encrypted=True,
            node_root_volume_size=40,
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
        self.register_outputs({
            "cluster_iam_role": self.cluster_iam_role,
            "instance_roles": self.instance_roles,
            "kubeconfig": self.cluster_kubeconfig
            #"node_group": self.node_group,
        })