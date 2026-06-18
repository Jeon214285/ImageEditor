from mlflow.tracking import MlflowClient

def get_champion_map(client: MlflowClient, model_name: str) -> float:
    try:
        champion = client.get_model_version_by_alias(model_name, 'champion')
        champion_run = client.get_run(champion.run_id)

        metric_key = 'metrics/mAP50-95_B'
        champion_map = champion_run.data.metrics.get(metric_key, -1.0)
        return champion_map
        
    except Exception as e:
        print(f"ERROR: EXCEPTION={e}")
        return -1.0
    
def promote_if_better(new_version, new_map, model_name):
    client = MlflowClient()
    current_champion_map = get_champion_map(client, model_name)

    print(f"INFO: [PROMOTION] current champion MAP={current_champion_map}")

    if new_map > current_champion_map:
        client.set_registered_model_alias(
            name=model_name,
            alias='champion',
            version=str(new_version)
        )
        print(f"INFO: {model_name} [PROMOTION] version {new_version} promoted to champion")
    else:
        print(f"INFO: [PROMOTION] {model_name} champion unchanged")