def test_metrics_endpoint_exists(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    # Prometheus format usually contains '# HELP' or '# TYPE'
    assert b"#" in res.data
