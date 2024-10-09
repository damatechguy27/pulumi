# #working deploy classic LB 
# # Deploy NGINX Ingress Controller using local Helm chart
# nginx_ingress = k8s.helm.v3.Release("nginx-ingress",
#     chart="./charts/ingress-nginx",  # Path to your local chart
#     namespace="ingress-nginx",
#     create_namespace=True,
#     values={
#         "controller": {
#             "service": {
#                 "type": "LoadBalancer",
#                 "externalTrafficPolicy": "Local"
#             },
#             "config": {
#                 "use-forwarded-headers": "true"
#             },
#             "metrics": {
#                 "enabled": "true"
#             }
#         }
#     },
#     opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider)
# )

# # Export the Load Balancer hostname
# ingress_service = k8s.core.v1.Service.get(
#     "ingress-nginx-controller-service",
#     f"{nginx_ingress.namespace}/ingress-nginx-controller",    
#     opts=pulumi.ResourceOptions(provider=cluster1.k8s_provider, depends_on=[nginx_ingress])
# )

# #pulumi.export("load_balancer_hostname", ingress_service.status.apply(lambda s: s.load_balancer.ingress[0].hostname))
# pulumi.export("load_balancer_hostname", ingress_service.status.load_balancer.ingress[0].hostname)
