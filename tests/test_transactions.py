"""Tests for transaction endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestTransactions:
    """Test suite for transaction endpoints."""

    def test_create_transaction_success(self, client: TestClient, registered_user: dict, 
                                       bank_account_data: dict, transaction_data: dict):
        """Test creating a transaction."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account first
        account_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = account_response.json()["id"]
        
        # Create transaction
        transaction_data["account_id"] = account_id
        response = client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["account_id"] == account_id
        assert data["amount"] == transaction_data["amount"]
        assert data["category"] == transaction_data["category"]

    def test_create_transaction_invalid_account(self, client: TestClient, registered_user: dict, 
                                               transaction_data: dict):
        """Test creating transaction with invalid account fails."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        transaction_data["account_id"] = 99999
        response = client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        assert response.status_code == 404

    def test_create_transaction_no_auth(self, client: TestClient, transaction_data: dict):
        """Test creating transaction without authentication fails."""
        response = client.post("/api/v1/transactions", json=transaction_data)
        assert response.status_code == 401

    def test_list_transactions_empty(self, client: TestClient, registered_user: dict):
        """Test listing transactions when none exist."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/transactions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_transactions_success(self, client: TestClient, registered_user: dict,
                                      bank_account_data: dict, transaction_data: dict):
        """Test listing transactions."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        account_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = account_response.json()["id"]
        
        # Create transaction
        transaction_data["account_id"] = account_id
        client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        
        # List transactions
        response = client.get("/api/v1/transactions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == transaction_data["category"]

    def test_list_transactions_with_filters(self, client: TestClient, registered_user: dict,
                                           bank_account_data: dict, transaction_data: dict):
        """Test listing transactions with category filter."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        account_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = account_response.json()["id"]
        
        # Create transaction
        transaction_data["account_id"] = account_id
        client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        
        # Filter by category
        response = client.get("/api/v1/transactions?category=food", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Filter by non-matching category
        response = client.get("/api/v1/transactions?category=entertainment", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_transaction_success(self, client: TestClient, registered_user: dict,
                                    bank_account_data: dict, transaction_data: dict):
        """Test getting a specific transaction."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account and transaction
        account_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = account_response.json()["id"]
        transaction_data["account_id"] = account_id
        create_response = client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        transaction_id = create_response.json()["id"]
        
        # Get transaction
        response = client.get(f"/api/v1/transactions/{transaction_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id

    def test_get_transaction_not_found(self, client: TestClient, registered_user: dict):
        """Test getting non-existent transaction returns 404."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/transactions/99999", headers=headers)
        assert response.status_code == 404

    def test_transaction_summary_analytics(self, client: TestClient, registered_user: dict,
                                          bank_account_data: dict, transaction_data: dict):
        """Test transaction summary analytics endpoint."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        
        # Create account
        account_response = client.post("/api/v1/accounts", json=bank_account_data, headers=headers)
        account_id = account_response.json()["id"]
        
        # Create multiple transactions
        transaction_data["account_id"] = account_id
        client.post("/api/v1/transactions", json=transaction_data, headers=headers)
        
        # Get summary
        response = client.get("/api/v1/transactions/analytics/summary?days=30", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_income" in data
        assert "transaction_count" in data
        assert "category_breakdown" in data
        assert data["transaction_count"] == 1
