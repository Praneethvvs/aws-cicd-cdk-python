from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda as lambda_,
    # aws_sqs as sqs,
    aws_apigateway as api_gateway
)
# https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.Bucket.html

from constructs import Construct
import typing


class ResourceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(self, "pvvs-json-data-bucket-logical-id",
                  bucket_name="pvvs-json-data-bucket",
                  versioned=False
                  )



        iam_json_data_s3_bucket_access_role = iam.Role(self, 'iam_json_data_s3_bucket_access',
                                                       role_name='s3accessLambda',
                                                       description='role for lambda to access to s3 bucket',
                                                       assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))

        iam_json_data_s3_bucket_access_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))

        read_json_lambda = lambda_.Function(self, 'read_json_lambda_function',
                                            runtime=typing.cast(lambda_.Runtime, lambda_.Runtime.PYTHON_3_7),
                                            handler='lambda_function.lambda_handler',
                                            code=lambda_.Code.from_asset('assets/'),
                                            role=iam_json_data_s3_bucket_access_role)

        api_lambda_access = api_gateway.LambdaRestApi(self, 'json-resp-api-gateway',
                                                      handler=read_json_lambda,
                                                      rest_api_name='json-read-api',
                                                      deploy=True,
                                                      proxy=False)

        readdata = api_lambda_access.root.add_resource("getdata")
        readdata.add_method("GET")
