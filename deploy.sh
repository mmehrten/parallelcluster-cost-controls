#! /bin/sh
set -e 

BUCKET="${1}"
if [ -z "${BUCKET}" ]; then
    echo "Please provide S3 bucket to upload artifacts to"
    exit 1
fi
for f in `ls src/`; do
    cd src
    zip -r "${f}.zip" "${f}/"
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
echo "  --template-url https://s3.amazonaws.com/mdmtempbkt/src/provision-core.yaml \\"
echo "  --parameters ParameterKey=ApproverARN,ParameterValue=arn:aws:iam::... \\"
echo "               ParameterKey=LambdaCodeS3Bucket,ParameterValue=${BUCKET} \\"
echo "  --capabilities CAPABILITY_NAMED_IAM"