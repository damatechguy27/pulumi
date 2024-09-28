import pulumi
import pulumi_aws as aws
from vpc import VPC
from eks import EKSCluster
from eks_iam_roles import cluster_role, node_group_role
from ami import ami
import pulumi_kubernetes as k8s


if __name__ == '__main__':

    vpc1 = VPC('vpc','10.0.0.0/16',2)


    cluster1 = EKSCluster(
        'Cluster1',
        vpc1.vpc.id,
        vpc1.public_subnets,
        'API_AND_CONFIG_MAP',
        "1.30",
        ['t3.medium'],
        2,
        2,
        2,
        opts=pulumi.ResourceOptions(depends_on=cluster_role)
        )

    # Export the kubeconfig
    #pulumi.export('kubeconfig', cluster1.cluster.kubeconfig)

    # Export the EKS cluster name
    #pulumi.export('cluster_name', cluster1.cluster.id)

    # # Export the cluster's kubeconfig
    # kubeconfig = cluster1.kubeconfig

    # # Create the Kubernetes provider using the extracted kubeconfig
    # k8s_provider = k8s.Provider("k8s", kubeconfig=kubeconfig)
        
    # #######################################
    # # Patching 
    # ######################################
    # # Patch Custom Resource Definitions (CRDs)
    # eniconfig_crd_patch = k8s.apiextensions.v1beta1.CustomResourceDefinitionPatch(
    #     "eniconfigs-crd-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="eniconfigs.crd.k8s.amazonaws.com"),
    #     spec=k8s.apiextensions.v1beta1.CustomResourceDefinitionSpecPatchArgs()
    # )

    # policyendpoints_crd_patch = k8s.apiextensions.v1beta1.CustomResourceDefinitionPatch(
    #     "policyendpoints-crd-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="policyendpoints.networking.k8s.aws"),
    #     spec=k8s.apiextensions.v1beta1.CustomResourceDefinitionSpecPatchArgs()
    # )

    # # Patch ServiceAccount
    # aws_node_svc_account_patch = k8s.core.v1.ServiceAccountPatch(
    #     "aws-node-svc-account-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="aws-node", namespace="kube-system"),
    # )

    # # Patch ConfigMap
    # vpc_cni_configmap_patch = k8s.core.v1.ConfigMapPatch(
    #     "vpc-cni-configmap-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="amazon-vpc-cni", namespace="kube-system"),
    # )

    # # Patch ClusterRole
    # aws_node_clusterrole_patch = k8s.rbac.v1.ClusterRolePatch(
    #     "aws-node-clusterrole-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="aws-node"),
    # )

    # # Patch ClusterRoleBinding
    # aws_node_clusterrolebinding_patch = k8s.rbac.v1.ClusterRoleBindingPatch(
    #     "aws-node-clusterrolebinding-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="aws-node"),
    # )

    # # Patch DaemonSet
    # aws_node_daemonset_patch = k8s.apps.v1.DaemonSetPatch(
    #     "aws-node-daemonset-patch",
    #     metadata=k8s.meta.v1.ObjectMetaPatchArgs(name="aws-node", namespace="kube-system"),
    #     spec=k8s.apps.v1.DaemonSetSpecPatchArgs()
    # )

    # # Stack outputs for verification
    # pulumi.export("eniconfig_crd_patch", eniconfig_crd_patch.metadata.name)
    # pulumi.export("policyendpoints_crd_patch", policyendpoints_crd_patch.metadata.name)
    # pulumi.export("aws_node_svc_account_patch", aws_node_svc_account_patch.metadata.name)
    # pulumi.export("vpc_cni_configmap_patch", vpc_cni_configmap_patch.metadata.name)
    # pulumi.export("aws_node_clusterrole_patch", aws_node_clusterrole_patch.metadata.name)
    # pulumi.export("aws_node_clusterrolebinding_patch", aws_node_clusterrolebinding_patch.metadata.name)
    # pulumi.export("aws_node_daemonset_patch", aws_node_daemonset_patch.metadata.name)