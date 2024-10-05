import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json

class newcluster(pulumi.ComponentResource):
    def __init__(self, name:str):
        super().__init__('custom:resource:newcluster', name)
        
        self.cluster = eks.Cluster(
            name,
            desired_capacity=1,
            min_size= 1,
            max_size= 2
        )

         # Store the IAM role and instance roles as output properties
        self.cluster_iam_role = self.cluster.instance_roles.apply(lambda roles: roles[0].arn)
        self.instance_roles = self.cluster.instance_roles


        # Create a Node Group using the service role and instance roles from the cluster
        # This Profile is passed into the V2 module to 
        self.instance_profile_name = aws.iam.InstanceProfile(
            f"{name}-instance-profile",
            role=self.instance_roles[0].name
        )


# managed Node group automatically makes the EBS root volume a GP3 
# automatically deploys nodes within a launch template
# and adds the role of the cluster, But does not automatically add the tags with hash
        self.node_group = eks.ManagedNodeGroup(
            f"{name}-node-group",
            cluster=self.cluster,
            node_role=self.instance_roles[0],
            instance_types=["t3.medium"],
            scaling_config=aws.eks.NodeGroupScalingConfigArgs(
                desired_size=1,
                min_size=1,
                max_size=2,
            ),
            #instance_profile=instance_profile_arn,
            opts=pulumi.ResourceOptions(parent=self)
        )

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
            "node_group": self.node_group,
        })