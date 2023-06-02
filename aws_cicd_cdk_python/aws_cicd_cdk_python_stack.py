from aws_cdk import (
    # Duration,
    Stage,
    Stack,
    pipelines,
    aws_codepipeline as codepipeline,
    Environment
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

        git_input = pipelines.CodePipelineSource.connection(
            repo_string="Praneethvvs/aws-cicd-cdk-python",
            branch="main",
            connection_arn="arn:aws:codestar-connections:us-east-1:578893893191:connection/a427e126-3adf-4175-9f32-4ea752206575"
        )


        #define pipeline
        code_pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="aws-cicd-cdk-pipeline",
            cross_account_keys=False
        )

        synth_step = pipelines.ShellStep(
            id="Synth",
            install_commands=[
                'pip install -r requirements.txt'
            ],
            commands=['npm ci',
                      'npm run build',
                      'npx cdk synth'],

            input=git_input
        )

        #create pipeline
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
