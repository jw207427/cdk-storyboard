import aws_cdk as cdk
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_iam as iam,
)
from constructs import Construct

class StoryboardAPIStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the role for the Lambda function to invoke SageMaker
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSageMakerFullAccess"
                )
            ],
        )

        # Create the Lambda Layer
        boto3_layer = lambda_.LayerVersion(self, "Boto3UpdateLayer",
            code=lambda_.Code.from_asset("./layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        pillow_layer = lambda_.LayerVersion.from_layer_version_arn(self, 
            "PillowLayer", 
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-pillow:1"
        )

        # Define the Lambda function
        lambda_fn = lambda_.Function(
            self,
            "StoryboardLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(300),  # Set timeout to 300 seconds (5 minutes)
            memory_size=128,  # Set memory size to 1024 MB (1 GB)
            code=lambda_.Code.from_asset("storyboard_generator"),
            handler="lambda_function.lambda_handler",
            role=lambda_role,
            layers=[boto3_layer, pillow_layer]
        )

        # Create the IAM role for API Gateway CloudWatch Logs
        api_gateway_cloudwatch_logs_role = iam.Role(
            self, "APIGatewayCloudWatchLogsRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonAPIGatewayPushToCloudWatchLogs")
            ]
        )

        # Define the API Gateway
        api = apigw.RestApi(
            self,
            "StoryboardAPI",
            rest_api_name="Storyboard API",
            description="This API generates storyboard images from text prompts.",
            deploy_options=apigw.StageOptions(
                data_trace_enabled=True,
                metrics_enabled=True,
                logging_level=apigw.MethodLoggingLevel.INFO,
                throttling_burst_limit=5,
                throttling_rate_limit=10,
            ),
        )

        # Associate the CloudWatch role with the API Gateway account
        apigw.CfnAccount(self, "APIGatewayAccount",
            cloud_watch_role_arn=api_gateway_cloudwatch_logs_role.role_arn
        )

        # Define the POST method for the API
        post_integration = apigw.LambdaIntegration(
            lambda_fn,
            proxy=False,
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                )
            ],
            request_templates={
                "application/json": '{"statusCode": 200}'
            },
        )

        api.root.add_resource("storyboard").add_method(
            "POST",
            post_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )