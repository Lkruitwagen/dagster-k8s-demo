# dagster-k8s-demo
This demo sends a dad joke to a slack channel of your choice every 5 minutes.
It is also a complete example for deploying a Dagster orchestration suite via a kubernetes (k8s) cluster on Google's Kubernetes Engine. 
This is a starting point for building a full back-end data engineering infrastructure, using Dagster as the orchestration framework, control entrypoint, and UI.
This repo roughly follows the [Deploying Dagster with Helm Guide](https://docs.dagster.io/deployment/guides/kubernetes/deploying-with-helm), also incorporating the [Deploying Dagster to GCP](https://docs.dagster.io/deployment/guides/gcp) tips.

To use this repo, you must have a [slackbot built](https://medium.com/applied-data-science/how-to-build-you-own-slack-bot-714283fd16e5) and have admin access to a GCP project.

This code accompanies the blog post here (coming soon), which describes in detail how to build and deploy this codebase, and why it's useful.

## Development - user code

The user code in this repo is a simple dagsterified computation graph, representing any abstract workflow you choose.
In this case it retrieves a dad joke from [http://icanhazdadjoke.com] and forwards it to a slack channel.
The user must install the slackbot to this slack channel.

For local development, this repo can be installed with:

    pip install -e .[dev]

Test-driven development can use pytest to run the example pipeline locally:

    pytest -xs

Environment variables will need to be set, matching the template in `.env.template`. 
These varibles can be set with:

    source .env

## Deployment - Dagster k8s cluster

This simple (annoying!) computation pipeline can be deployed to Googe Kubernetes Engine following the complete guide in the blog post here (coming soon).

Here are the quick instructions:
1. create a cloud-build trigger to containerise this code on Google Container Registry or a container registry of your choice
2. launch a cloud-sql postgresql instance, give it a private IP address, and create a database
3. create a storage bucket and folder with the bucket name and prefix found in `k8s_config.yaml`
4. give the compute engine default service account `storage admin` and `artifact registry admin` roles
5. launch a k8s cluster on GKE, allowing the nodes access to cloud storage and cloud sql
6. install and configure `kubectl` to give your local terminal control of the GKE cluster
7. add secret values to your k8s cluster: `dagster-slackbot-token`, `dagster-slackbot-channel`, and `dagster-postgresql-secret`, using `kubectl create secret generic <secret-key> --from-literal=<env-key>=<env-val>`
8. copy `helm-template.yaml` to `helm.yaml` and add your postgresql instance private ip address, your database name, and user code container address.
9. deploy this helm chart to your cluster with `helm upgrade --install dagster dagster/dagster -f helm.yaml`
10. use `kubectl port-forward <webserved-pod-name> 8080:80` to inspect your orchestration and deploy the schedule
11. watch the dad jokes roll in, chuckling in disgust

