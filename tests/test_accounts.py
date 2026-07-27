"""Tests for bank account endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestBankAccounts:
    """Test suite for bank account endpoints."""

    def test_create_account_success(self, client: TestClient, registered_user: dict, bank_account_data: dict):
        """Test creating a bank account."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["account_name"] == bank_account_data["account_name"]
        assert data["balance"] == bank_account_data["balance"]
        assert data["user_id"] == registered_user["user"]["id"]
        assert "id" in data

    def test_create_account_no_auth(self, client: TestClient, bank_account_data: dict):
        """Test creating account without authentication fails."""
        response = client.post("/api/v1/accounts", json=bank_account_data)
        assert response.status_code == 401

    def test_list_accounts_empty(self, client: TestClient, registered_user: dict):
        """Test listing accounts when none exist."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/accounts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_accounts_success(self, client: TestClient, registered_user: dict, bank_account_data: dict):
        """Test listing bank accounts."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        
        # List accounts
        response = client.get("/api/v1/accounts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["account_name"] == bank_account_data["account_name"]

    def test_get_account_success(self, client: TestClient, registered_user: dict, bank_account_data: dict):
        """Test getting a specific account."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        create_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = create_response.json()["id"]
        
        # Get account
        response = client.get(f"/api/v1/accounts/{account_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["account_name"] == bank_account_data["account_name"]

    def test_get_account_not_found(self, client: TestClient, registered_user: dict):
        """Test getting non-existent account returns 404."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/accounts/99999", headers=headers)
        assert response.status_code == 404

    def test_update_account_success(self, client: TestClient, registered_user: dict, bank_account_data: dict):
        """Test updating a bank account."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        create_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = create_response.json()["id"]
        
        # Update account
        update_data = {"account_name": "Updated Checking", "balance": 7500.00}
        response = client.put(f"/api/v1/accounts/{account_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "Updated Checking"
        assert data["balance"] == 7500.00

    def test_delete_account_success(self, client: TestClient, registered_user: dict, bank_account_data: dict):
        """Test deleting a bank account."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        create_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = create_response.json()["id"]
        
        # Delete account
        response = client.delete(f"/api/v1/accounts/{account_id}", headers=headers)
        assert response.status_code == 204
        
        # Verify account is deleted
        get_response = client.get(f"/api/v1/accounts/{account_id}", headers=headers)
        assert get_response.status_code == 404
