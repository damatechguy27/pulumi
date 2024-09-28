# import pulumi
# import pulumi_aws as aws
# from pulumi_aws import ec2
# from eks_iam_roles import node_group_role, nodegroup_profile

# ami = aws.ec2.get_ami(
#     most_recent=True,
#     owners=['amazon'],
#     filters=[{"name":"name","values":["amzn2-ami-hvm-*-x86_64-ebs"]}
#              ])

# # Define the IAM Instance Profile
# #instance_profile = aws.iam.InstanceProfile("nodeGroupInstanceProfile", role=role.name)

# launch_temp1 = aws.ec2.LaunchTemplate("myLaunchTemplate",
#     image_id=ami.id,  # Use an appropriate AMI for your region and instance type
#     instance_type="t3.medium",
#     block_device_mappings=[{
#         "device_name": "/dev/xvda",
#         "ebs": {
#             "volume_size": 20,  # Specify the desired root volume size
#             "volume_type": "gp3",  # Specify the desired volume type
#             "delete_on_termination": True,
#             "encrypted": "true"
#         },
#     }],
#     iam_instance_profile={
#         "name": nodegroup_profile.name
#     },
# )


# # Export the necessary attributes

# pulumi.export("launchTemplateName", launch_temp1.name)
# #pulumi.export('launch_template_id', launch_temp1.id)