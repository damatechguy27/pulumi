import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
from ami import ami
from eks_iam_roles import cluster_role, node_group_role, nodegroup_profile, cluster_profile

class EKSCluster(pulumi.ComponentResource):
    def __init__(self, name: str, vpc_id: str, subnet_ids: list, authentication_mode: str,
                 version: str, instance_type: list, desired_capacity: int, min_size: int, max_size: int, opts=None):
        super().__init__('custom:resource:EKSCluster', name, {}, opts)
        
        # Create the cluster
        self.cluster_role = cluster_role
        self.node_group_role = node_group_role
        self.cluster = eks.Cluster(
            name,
            service_role=self.cluster_role,
            skip_default_node_group=True,
            create_oidc_provider=True,
            vpc_id=vpc_id,
            public_subnet_ids=subnet_ids,
            authentication_mode=eks.AuthenticationMode.API_AND_CONFIG_MAP,
            access_entries= {
                f'{cluster_role}': eks.AccessEntryArgs(
                                    principal_arn=cluster_role.arn,
                                    #  kubernetes_groups=["test-group"], access_policies={
                                    #      'view': eks.AccessPolicyAssociationArgs(
                                    #          policy_arn="arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy",
                                    #          access_scope=aws.eks.AccessPolicyAssociationAccessScopeArgs(namespaces=["default", "application"], type="namespace")
                                    #      ),
                                    # }
                                    type= eks.AccessEntryType.EC2_LINUX,
                                )    
            },
            version=version,
            instance_role=self.node_group_role,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Add the VPC CNI, Core DNS, and Kube Proxy addons
        self.addon1 = eks.Addon(
            "vpc-cni",
            cluster=self.cluster,
            addon_name="vpc-cni",
            addon_version="v1.18.3-eksbuild.3",
            opts=pulumi.ResourceOptions(parent=self.cluster)
        )
        
        self.addon2 = eks.Addon(
            "core-dns",
            cluster=self.cluster,
            addon_name="core-dns",
            addon_version="v1.10.1-eksbuild.13",
            opts=pulumi.ResourceOptions(parent=self.cluster)
        )
        
        self.addon3 = eks.Addon(
            "kube-proxy",
            cluster=self.cluster,
            addon_name="kube-proxy",
            addon_version="v1.28.12-eksbuild.5",
            opts=pulumi.ResourceOptions(parent=self.cluster)
        )


        self.cluster_temp = aws.ec2.LaunchTemplate(f"{name}-Launch-Template",
            image_id=ami.id,  # Use an appropriate AMI for your region and instance type
            instance_type="t3.medium",
            block_device_mappings=[{
                "device_name": "/dev/xvda",
                "ebs": {
                    "volume_size": 20,  # Specify the desired root volume size
                    "volume_type": "gp3",  # Specify the desired volume type
                    "delete_on_termination": True,
                    "encrypted": True
                },
            }],
            # iam_instance_profile={
            #     "name": nodegroup_profile.name
            # },
        )
        
        # self.node_group=eks.NodeGroupV2(
        #     "cluster1-ng",
        #     cluster=self.cluster.core,
        #     desired_capacity=desired_capacity,
        #     min_size=min_size,
        #     max_size=max_size,
        #     node_root_volume_encrypted=True,
        #     node_root_volume_type="gp3",
        #     node_root_volume_size=20,


        # )

        # Define the managed node group
        self.managed_nodegroup = eks.ManagedNodeGroup(
            f"{name}-MNG",
            cluster=self.cluster.core,
            node_role=node_group_role,
            #cluster_name=self.cluster._name,
            #node_group_name=self.node_group.name,
            #instance_types=instance_type,
            launch_template={
                "id": self.cluster_temp,
                "version": '$Latest',
            },
            scaling_config=aws.eks.NodeGroupScalingConfigArgs(
                desired_size=desired_capacity,
                min_size=min_size,
                max_size=max_size,
            ),
            subnet_ids = subnet_ids,
            opts=pulumi.ResourceOptions(parent=self.cluster)
        )

        # Export the cluster's kubeconfig and endpoint as stack outputs
        pulumi.export("cluster_name", self.cluster.name)
       # pulumi.export("cluster_endpoint", self.cluster.endpoint)
        pulumi.export("kubeconfig", self.cluster.kubeconfig)
        
        # k8s_provider=k8s(
        #     "cluster1-provider",
        #     kubeconfig=self.cluster.kubeconfig,
        #     opts=child_opts
        # )
       # self.register_outputs({})


    

