import pulumi
import pulumi_aws as aws
from pulumi_aws import ec2



class VPC(pulumi.ComponentResource):
    def __init__(self,name:str, cidr_block:str, number_of_subnets:int, opts=None):
        super().__init__('custom:resource:Vpc',name,{}, opts)

        self.vpc = aws.ec2.Vpc(name, 
                    cidr_block = cidr_block,
                    enable_dns_support=True,
                    enable_dns_hostnames=True,
                    tags={"Name":f'Pulumi-{name}'}
                    )
        
        self.intgw= aws.ec2.InternetGateway(f'Pulumi-{name}-IntGW',
                                            vpc_id=self.vpc.id,
                                            tags={"Name":f'Pulumi-{name}-IntGw'}
                                            )
        
           # Create public subnets and associate them with route tables that have routes to the Internet Gateway
        self.public_subnets = []
        for i in range(number_of_subnets):  # Example for two subnets
            subnet = aws.ec2.Subnet(f"Pulumi-{name}-public-{i}",
                                vpc_id=self.vpc.id,
                                cidr_block=f"10.0.{i}.0/24",
                                map_public_ip_on_launch=True,
                                availability_zone=f"us-west-2{chr(97 + i)}",  # Adjust for your region
                                tags={"Name": f"Pulumi-{name}-public-{i}"})
            self.public_subnets.append(subnet)

            # Route table for the public subnet
            rt = aws.ec2.RouteTable(f"Pulumi-{name}-rt-public-{i}",
                                vpc_id=self.vpc.id,
                                routes=[ec2.RouteTableRouteArgs(
                                    cidr_block="0.0.0.0/0",
                                    gateway_id=self.intgw.id
                                )],
                                tags={"Name": f"Pulumi-{name}-rt-public-{i}"})
            
            aws.ec2.RouteTableAssociation(f"Pulumi-{name}-rta-public-{i}",
                                      subnet_id=subnet.id,
                                      route_table_id=rt.id)

    def describe(self):
        return f"VPC Name: Pulumi-{self.name}"    