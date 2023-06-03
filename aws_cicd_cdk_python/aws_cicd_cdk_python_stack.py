from aws_cdk import (
    # Duration,
    Stage,
    Stack,
    pipelines,
    aws_codepipeline as codepipeline,
    Environment,
    SecretValue
    # aws_sqs as sqs,
)
from constructs import Construct
from aws_cicd_cdk_python.resources_stack import ResourceStack


class DeployStage(Stage):
    def __init__(self, scope: Construct, id: str, env: Environment, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)
        ResourceStack(self, 'ResourceStack', env=env, stack_name="resource-stack-deploy")


class AwsCicdCdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # define pipeline
        code_pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="aws-cicd-cdk-pipeline",
            cross_account_keys=False
        )

        # define synth step
        synth_step = pipelines.ShellStep(
            id="Synth",
            install_commands=[
                'pip install -r requirements.txt'
            ],
            commands=[
                'npx cdk synth'],

            input=pipelines.CodePipelineSource.git_hub('Praneethvvs/aws-cdk-cicd-python', 'git-PAT-authentication',
                                                       authentication=SecretValue.secrets_manager(
                                                           "arn:aws:secretsmanager:us-east-1:578893893191:secret:github-token-aws-irxNiZ"))

        )

        # create pipeline
        pipeline = pipelines.CodePipeline(
            self, 'CodePipeline',
            self_mutation=True,
            code_pipeline=code_pipeline,
            synth=synth_step
        )

        deployment_wave = pipeline.add_wave("DeploymentWave")

        deployment_wave.add_stage(DeployStage(
            self, 'DeployStage',
            env=(Environment(account='578893893191', region='us-east-1'))
        ))
