import pulumi
import pulumi_aws as aws

# Create an ECR repository
repo = aws.ecr.Repository('pulumi_ecr_repo')

# Export the repository URL
pulumi.export('repository_url', repo.repository_url)
