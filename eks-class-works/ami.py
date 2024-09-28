import pulumi
import pulumi_aws as aws
from pulumi_aws import ec2

ami = aws.ec2.get_ami(
    most_recent=True,
    owners=['amazon'],
    filters=[{"name":"name","values":["amzn2-ami-hvm-*-x86_64-ebs"]}
             ])