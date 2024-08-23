# Getting Started

## Step 1: Install AWS IoT Greengrass Core software with automatic resource provisioning on the edge device

There are two possible ways of installing AWS Iot Greengrass Core software:

- Manually following the [AWS documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/quick-installation.html)
- Automatically using Ansible

> [!WARNING]  
> The installation with Ansible works for Unix OS **only**!

### Add the IP of your device to the Ansible inventory

Open the [Ansible inventory file](../../edge/aws/ansible/inventories/hosts) and add your device in it.

### Run the playbook to install all required softwares automatically on your device

Go to the folder and create yourself a Python virtual environment if you don't have any:
```shell
cd ../../edge/aws/ansible/
python -m venv .venv
```

Activate the Python virtual environment and install the required libraries:
```shell
source .venv/bin/activate
pip install -r requirements.txt
```

Apply the Ansible playbook on your device to install all required softwares:
```shell
ansible-playbook -i inventories/hosts playbooks/setup_the_device_environment_for_aws_iot_greengrass_core_software.yml 
```

## Step 2: Register your device to AWS

Follow the [AWS documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-quick-start.html) to register your device.

## Step 3: Create the resources in AWS

### Upload the components to S3 and ECR

#### Create the AWS S3 bucket and upload the artifact

Replace `AWS_ACCOUNT_ID` with your AWS account ID and `REGION` with the AWS Region:

```shell
aws s3 mb s3://greengrass-component-artifacts-AWS_ACCOUNT_ID-REGION
aws s3 cp docker-compose.yml s3://greengrass-component-artifacts-AWS_ACCOUNT_ID-REGION/artifacts/1.0.0/docker-compose.yml
```

#### Create the AWS ECR repository

Replace `AWS_ACCOUNT_ID` with your AWS account ID and `REGION` with the AWS Region:

```shell
aws ecr create-repository --registry-id AWS_ACCOUNT_ID --region REGION --repository-name vio/file_uploader
```

#### Push the Docker image to ECR repository

Replace `AWS_ACCOUNT_ID` with your AWS account ID and `REGION` with the AWS Region:

```shell
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin AWS_ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com
docker build -t AWS_ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/vio/file_uploader:latest
docker push AWS_ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/vio/file_uploader:latest
```

### Allow the core device to access component artifacts in the S3 bucket and ECR

#### Create the policy to access S3 and ECR

```shell
aws iam create-policy \     
  --policy-name MyGreengrassV2ComponentArtifactPolicy \
  --policy-document file://component-artifact-policy.json 
```

#### Attach the policy to the core device role

Replace GreengrassV2TokenExchangeRole with the name of the role for the core device:

```shell
aws iam attach-role-policy \\
  --role-name GreengrassV2TokenExchangeRole \\
  --policy-arn arn:aws:iam::123456789012:policy/MyGreengrassV2ComponentArtifactPolicy
```

## Step 4: Create a component resource in AWS IoT Greengrass from the recipe

### Add the artifact's Amazon S3 URI to the component recipe.

Open the YAML recipe file [fu_recipe.yaml](../greengrassv2/fu_recipe.yaml) and update the line concerning the artifacts with:

```yaml
Artifacts:
  - URI: s3://greengrass-component-artifacts-AWS_ACCOUNT_ID-REGION/artifacts/1.0.0/docker-compose.yml
```

### Create the component resource in AWS IoT Greengrass from the recipe

```shell
aws greengrassv2 create-component-version --inline-recipe fileb://recipes/fu_recipe.yaml
```

The response looks similar to the following example if the request succeeds.

```json
{
  "arn": "arn:aws:greengrass:REGION:AWS_ACCOUNT_ID:components:file_uploader:versions:1.0.0",
  "componentName": "file_uploader",
  "componentVersion": "1.0.0",
  "creationTimestamp": "Mon Nov 30 09:04:05 UTC 2020",
  "status": {
    "componentState": "REQUESTED",
    "message": "NONE",
    "errors": {}
  }
}
```

Copy the `arn` from the output to check the state of the component and verify it is deployable. Replace the `ARN` with the one copied and type:


```shell
aws greengrassv2 describe-component --arn "arn:aws:greengrass:REGION:AWS_ACCOUNT_ID:components:file_uploader:versions:1.0.0"
```

If the component validates, the response indicates that the component state is DEPLOYABLE.

```json
{
  "arn": "arn:aws:greengrass:REGION:AWS_ACCOUNT_ID:components:file_uploader:versions:1.0.0",
  "componentName": "file_uploader",
  "componentVersion": "1.0.0",
  "creationTimestamp": "2020-11-30T18:04:05.823Z",
  "publisher": "Amazon",
  "description": "My first Greengrass component.",
  "status": {
    "componentState": "DEPLOYABLE",
    "message": "NONE",
    "errors": {}
  },
  "platforms": [
    {
      "os": "linux",
      "architecture": "all"
    }
  ]
}
```


## Step 5: Deploy the component

Edit the JSON deployment file [deployment-revision-1-for-bapo-group.json](deployment-revision-1-for-bapo-group.json) to set correctly the bucket name and run the following command to deploy the component to your Greengrass core device replacing `MyGreengrassCore` with the name of the AWS IoT thing for your core device:

```shell
aws greengrassv2 create-deployment \
  --target-arn "arn:aws:iot:REGION:AWS_ACCOUNT_ID:thing/MyGreengrassCore" \
  --cli-input-json file://deployment-revision-1-for-bapo-group.json
```

### Create a deployment

Please refer to the [AWS documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-deployments.html).