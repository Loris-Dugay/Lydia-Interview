from dagster import ScheduleDefinition

from orchestration.jobs.crypto_pipeline import crypto_pipeline_job

daily_crypto_pipeline_schedule = ScheduleDefinition(
    job=crypto_pipeline_job, cron_schedule="0 12 * * *", name="daily_crypto_pipeline"
)
