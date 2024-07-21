import pulumi
import pulumi_aws as aws

# Create an ECR repository
repo = aws.ecr.Repository('PulumiECRRepo')

# Export the repository URL
pulumi.export('repository_url', repo.repository_url)
