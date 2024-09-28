# import pulumi
# import pulumi_aws as aws
# import pulumi_eks as eks
# import pulumi_kubernetes as k8s
# from launch_temp import ami, launch_temp1
# from eks_iam_roles import cluster_role, node_group_role, nodegroup_profile, cluster_profile

# class EKSCluster(pulumi.ComponentResource):
#     def __init__(self, name: str, vpc_id: str, subnet_ids: list, authentication_mode: str,
#                  version: str, instance_type: list, desired_capacity: int, min_size: int, max_size: int, opts=None):
#         super().__init__('custom:resource:EKSCluster', name, {}, opts)
        
#         # Create the cluster
#         self.cluster_role = cluster_role
#         self.node_group_role = node_group_role
#         self.cluster = eks.Cluster(
#             name,
#             service_role=self.cluster_role,
#             create_oidc_provider=True,
#            # vpc_id=vpc_id,
#             subnet_ids=subnet_ids,
#             version=version,
#             opts=pulumi.ResourceOptions(parent=self)
#         )
        
#         # Add the VPC CNI, Core DNS, and Kube Proxy addons
#         self.addon1 = eks.Addon(
#             "vpc-cni",
#             cluster=self.cluster.eks_cluster.name,
#             addon_name="vpc-cni",
#             addon_version="v1.18.3-eksbuild.3",
#             opts=pulumi.ResourceOptions(parent=self.cluster)
#         )
        
#         self.addon2 = eks.Addon(
#             "core-dns",
#             cluster=self.cluster.eks_cluster.name,
#             addon_name="core-dns",
#             addon_version="v1.10.1-eksbuild.13",
#             opts=pulumi.ResourceOptions(parent=self.cluster)
#         )
        
#         self.addon3 = eks.Addon(
#             "kube-proxy",
#             cluster=self.cluster.eks_cluster.name,
#             addon_name="kube-proxy",
#             addon_version="v1.28.12-eksbuild.5",
#             opts=pulumi.ResourceOptions(parent=self.cluster)
#         )
        
#         # Define the managed node group
#         self.nodegroup = eks.ManagedNodeGroup(
#             "cluster1-NG",
#             cluster=self.cluster,
#             node_role_arn=node_group_role.arn,
#             instance_types=instance_type,
#             launch_template={
#                 "id": launch_temp1.id,
#                 "version": '$Latest',
#             },
#             scaling_config=aws.eks.NodeGroupScalingConfigArgs(
#                 desired_size=desired_capacity,
#                 min_size=min_size,
#                 max_size=max_size,
#             ),
#             opts=pulumi.ResourceOptions(parent=self.cluster)
#         )

#         # Export the cluster's kubeconfig and endpoint as stack outputs
#         pulumi.export("cluster_name", self.cluster.name)
#         pulumi.export("cluster_endpoint", self.cluster.endpoint)
#         pulumi.export("kubeconfig", self.cluster.kubeconfig)
        
#         # k8s_provider=k8s(
#         #     "cluster1-provider",
#         #     kubeconfig=self.cluster.kubeconfig,
#         #     opts=child_opts
#         # )
#        # self.register_outputs({})


    

