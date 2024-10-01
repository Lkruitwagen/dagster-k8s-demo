from dagster_demo.run import local_job


def test_example_project():
    assert local_job.execute_in_process().success