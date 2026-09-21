from __future__ import annotations

import hashlib
import hmac
import json

from whatsapp_ecosystem import WhatsAppEcosystem, WhatsAppWebhook


def test_register_login_and_weekly_expense(tmp_path):
    app = WhatsAppEcosystem(str(tmp_path / "test.db"))
    assert app.register("alice", "+100000000", "alice@example.com", "secret")
    assert app.login("alice", "secret")
    assert app.log_expense(12.5, "food", "sandwich")
    assert {row["category"]: row["total"] for row in app.get_weekly_summary()} == {"food": 12.5}
    app.close()


def test_webhook_challenge_and_event_parsing():
    webhook = WhatsAppWebhook("token")
    assert webhook.verify_challenge("subscribe", "token", "challenge") == (200, "challenge")
    body = json.dumps({"entry": [{"changes": [{"value": {"messages": [{"id": "m1"}]}}]}]}).encode()
    assert webhook.parse_event(body) == [{"id": "m1"}]


def test_webhook_signature():
    secret = "app-secret"
    body = b'{"entry": []}'
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    webhook = WhatsAppWebhook("token", secret)
    assert webhook.verify_signature(body, f"sha256={digest}")
    assert not webhook.verify_signature(body, "sha256=invalid")
