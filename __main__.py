import pulumi
import pulumi_aws as aws

# Create an ECR repository
repo = aws.ecr.Repository('Pulumi-ecr-repo')

# Export the repository URL
pulumi.export('repository_url', repo.repository_url)
