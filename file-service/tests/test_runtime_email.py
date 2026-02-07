import notify

def test_unauthorized_upload_triggers_email(client, monkeypatch):
    # turn on runtime emails for THIS test
    monkeypatch.setenv("ENABLE_RUNTIME_EMAILS", "true")
    monkeypatch.setenv("EMAIL_RATE_LIMIT_SECONDS", "0")

    sent = []

    def fake_send_email(subject, body):
        sent.append((subject, body))

    # patch the actual send function so no SMTP happens
    monkeypatch.setattr(notify, "send_email_smtp", fake_send_email)

    # call your endpoint without auth header -> should 401 and trigger notify
    res = client.post("/dashboard/upload")
    assert res.status_code == 401

    assert len(sent) == 1
    subject, body = sent[0]
    assert "Unauthorized" in subject
    assert "status=401" in body

def test_server_error_triggers_email(client, monkeypatch):
    monkeypatch.setenv("ENABLE_RUNTIME_EMAILS", "true")
    monkeypatch.setenv("EMAIL_RATE_LIMIT_SECONDS", "0")

    sent = []
    monkeypatch.setattr(notify, "send_email_smtp", lambda s, b: sent.append((s, b)))

    res = client.get("/test/crash")
    assert res.status_code == 500
    assert len(sent) == 1
    assert "500" in sent[0][0] or "Unhandled" in sent[0][0]