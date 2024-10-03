import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests

from dagster import In, config_from_files, file_relative_path, graph, op, repository, ScheduleDefinition
from dagster_gcp.gcs.io_manager import gcs_pickle_io_manager
from dagster_gcp.gcs.resources import gcs_resource
from dagster_k8s import k8s_job_executor

@op
def get_joke():
    """ Fetch a joke from the icanhazdadjoke API """

    r = requests.get(
        "https://icanhazdadjoke.com/", 
        headers={"Accept": "application/json"}
    )
    r.raise_for_status()
    return r.json()

@op(ins={"joke": In(dict)})
def post_joke(joke):
    """ Use the Slack SDK to post the joke to a designated channel """

    slack_token = os.getenv("SLACK_TOKEN")
    channel = os.getenv("SLACK_CHANNEL")

    client = WebClient(token=slack_token)

    try:
        r = client.chat_postMessage(channel=channel, text=joke["joke"])
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'

    return "success"



@graph
def example_graph():
    joke = get_joke()
    post_joke(joke=joke)


local_job = example_graph.to_job(
    name="example_job",
    description="Example job. Use this for local development and testing.",
    config=config_from_files(
        [
            file_relative_path(__file__, os.path.join("..", "pipeline.yaml")),
        ]
    ),
)


pod_per_op_job = example_graph.to_job(
    name="pod_per_op_job",
    description="""
    Example job that uses the `k8s_job_executor` to run each op in a separate pod.
    """,
    resource_defs={"gcs": gcs_resource, "io_manager": gcs_pickle_io_manager},
    executor_def=k8s_job_executor,
    config=config_from_files(
        [
            file_relative_path(__file__, os.path.join("..", "k8s_config.yaml")),
            file_relative_path(__file__, os.path.join("..", "pipeline.yaml")),
        ]
    ),
)

fivemin_schedule = ScheduleDefinition(job=pod_per_op_job, cron_schedule="*/5 * * * *")


@repository
def example_repo():
    return [local_job, pod_per_op_job, fivemin_schedule]