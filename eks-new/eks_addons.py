import pulumi
import pulumi_aws as aws
import pulumi_eks as eks

class eks_Addons(pulumi.ComponentResource):
    def __init__(self, name:str, addon_name:str, cluster:str, version:str, serviceaccount:str):
        super().__init__('custom:resource:newcluster', name)

        self.Addon = eks.Addon(name,
                    cluster=cluster,
                    addon_name=addon_name,
                    addon_version=version,
                    service_account_role_arn=serviceaccount,
                    resolve_conflicts_on_create="OVERWRITE"
                    )