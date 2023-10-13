#! /bin/sh
set -e 

BUCKET="${1}"
if [ -z "${BUCKET}" ]; then
    echo "Please provide S3 bucket to upload artifacts to"
    exit 1
fi
for f in `ls src/`; do
    cd "src/${f}"
    zip -r "${f}.zip" *
    aws s3 cp "${f}.zip" "s3://${BUCKET}/src/"
    rm "${f}.zip"
    cd -
done
aws s3 cp provision-core.yaml "s3://${BUCKET}/src/provision-core.yaml"
aws s3 cp provision-project.yaml "s3://${BUCKET}/src/provision-project.yaml"

echo "CloudFormation dependencies uploaded to s3://${BUCKET}/src"
echo "You can now deploy the CloudFormation template for the core infrastructure:"
echo ""
echo " aws cloudformation create-stack \\"
echo "  --stack-name TestStack \\"
echo "  --template-url https://s3.amazonaws.com/${BUCKET}/src/provision-core.yaml \\"
echo "  --parameters ParameterKey=ApproverARN,ParameterValue=arn:aws:iam::... \\"
echo "               ParameterKey=LambdaCodeS3Bucket,ParameterValue=${BUCKET} \\"
echo "               ParameterKey=ParallelClusterAPIEndpoint,ParameterValue=https://######.execute-api.${AWS_DEFAULT_REGION}.amazonaws.com/prod"
echo "  --capabilities CAPABILITY_NAMED_IAM"

# REGION=us-east-1
# API_STACK_NAME=ParallelClusterAPI
# VERSION=3.7.0
# aws cloudformation create-stack \
#     --region ${REGION} \
#     --stack-name ${API_STACK_NAME} \
#     --template-url https://${REGION}-aws-parallelcluster.s3.${REGION}.amazonaws.com/parallelcluster/${VERSION}/api/parallelcluster-api.yaml \
#     --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
# aws cloudformation wait stack-create-complete --stack-name ${API_STACK_NAME} --region ${REGION}



#  aws cloudformation create-stack \
#   --stack-name TestStack \
#   --template-url https://s3.amazonaws.com/mdmtempbkt/src/provision-core.yaml \
#   --parameters ParameterKey=ApproverARN,ParameterValue=arn:aws:iam::344418890787:role/Admin \
#                ParameterKey=LambdaCodeS3Bucket,ParameterValue=mdmtempbkt \
#                ParameterKey=ParallelClusterAPIEndpoint,ParameterValue=https://9lvyqyhx4b.execute-api.us-east-1.amazonaws.com/prod \
#                ParameterKey=ParallelClusterAPIKey,ParameterValue=KeYndRF6CB3qI91EWvfXF4DfkX1FJMKZLgvfQJma \
#   --capabilities CAPABILITY_NAMED_IAM





# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Deny",
#       "Principal": "*",
#       "Action": "execute-api:Invoke",
#       "Resource": "arn:aws:execute-api:us-east-1:344418890787:9lvyqyhx4b/*/*/*",
#       "Condition": {
#         "StringNotLike": {
#           "aws:PrincipalArn": [
#             "arn:aws:*::344418890787:*/ParallelClusterApiUserRole-5e67c7e0-5e48-11ee-b1c6-0e56311d0e19*",
#             "arn:aws:*::344418890787:*/hpc_*",
#             "arn:aws:*::344418890787:*/hpc_*/*",
#             "arn:aws:sts::344418890787:assumed-role/hpc_provision_cluster_handler/hpc_provision_cluster_handler",
#             "arn:aws:iam::344418890787:role/hpc_provision_cluster_handler"
#           ]
#         }
#       }
#     }
#   ]
# }