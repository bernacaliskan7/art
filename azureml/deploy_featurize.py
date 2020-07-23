import os

from azureml.core import Datastore
from azureml.core import Experiment, Workspace
from azureml.core.compute import ComputeTarget
from azureml.core.compute.amlcompute import AmlComputeProvisioningConfiguration
from azureml.train.estimator import Estimator

ws = Workspace(
    subscription_id="f9b96b36-1f5e-4021-8959-51527e26e6d3",
    resource_group="marhamil-mosaic",
    workspace_name="mosaic-aml"
)

datastore = Datastore.register_azure_blob_container(
    workspace=ws,
    datastore_name='mosaic_datastore',
    container_name='mosaic',
    account_name='mmlsparkdemo',
    sas_token="?sv=2019-02-02&ss=bf&srt=sco&sp=rlc&se=2030-01-23T04:14:29Z"
              "&st=2020-01-22T20:14:29Z&spr=https,http&sig=nPlKziG9ppu4Vt5"
              "b6G%2BW1JkxHYZ1dlm39mO2fMZlET4%3D",
    create_if_not_exists=True)

cluster_name = "training-4"
try:
    # Connecting to pre-existing cluster
    compute_target = ComputeTarget(ws, cluster_name)
    print("Found existing cluster...")
except:
    # Create a new cluster to train on
    provisioning_config = AmlComputeProvisioningConfiguration(
        vm_size="Standard_D4_v2",
        min_nodes=0,
        max_nodes=1
    )
    compute_target = ComputeTarget.create(ws, cluster_name, provisioning_config)
compute_target.wait_for_completion(show_output=True)

# Create and run the experiment
exp = Experiment(workspace=ws, name='featurize_artwork_4')

estimator = Estimator(
    source_directory=".",
    entry_script="featurize.py",
    script_params={
        "--data-dir": datastore.as_mount()
    },
    conda_dependencies_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "myenv.yml"),
    use_docker=True,
    custom_docker_image="typingkoala/mosaic_base_image:1.0.0",
    compute_target=compute_target
)

run = exp.submit(estimator)
run.wait_for_completion(show_output=True)

# Save the balltrees made in score.py and metadata
run.register_model(
    model_name="mosaic_model_4",
    model_path="outputs/"
)