from dagster import AssetSelection, define_asset_job

crypto_pipeline_job = define_asset_job(
    name="crypto_pipeline",
    # selection=AssetSelection.groups("extraction"),
    selection=AssetSelection.all(),
    description="Test extraction pipeline",
)
