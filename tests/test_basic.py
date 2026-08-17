import os
from whatsapp_ecosystem import WhatsAppEcosystem


def test_register_and_login(tmp_path):
    db = tmp_path / "test.db"
    app = WhatsAppEcosystem(db_path=str(db))

    username = "alice"
    phone = "+100000000"
    email = "alice@example.com"
    password = "secret"

    uid = app.register(username, phone, email, password)
    assert uid is not None

    ok = app.login(username, password)
    assert ok

    # log an expense
    eid = app.log_expense(12.5, "food", "sandwich")
    assert eid is not None

    summary = app.get_weekly_summary()
    # find food category
    totals = {row['category']: row['total'] for row in summary}
    assert totals.get('food') == 12.5

    app.close()
