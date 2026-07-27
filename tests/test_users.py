"""Tests for user management endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestUsers:
    """Test suite for user management endpoints."""

    def test_get_profile_success(self, client: TestClient, registered_user: dict):
        """Test getting user profile."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == registered_user["user"]["id"]
        assert data["email"] == registered_user["user"]["email"]
        assert data["username"] == registered_user["user"]["username"]

    def test_get_profile_no_auth(self, client: TestClient):
        """Test getting profile without authentication fails."""
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client: TestClient):
        """Test getting profile with invalid token fails."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 401

    def test_get_user_by_id(self, client: TestClient, registered_user: dict):
        """Test getting user by ID."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        user_id = registered_user["user"]["id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id

    def test_get_user_not_found(self, client: TestClient, registered_user: dict):
        """Test getting non-existent user returns 404."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/users/99999", headers=headers)
        assert response.status_code == 404

    def test_list_users(self, client: TestClient, registered_user: dict, test_user_data_2: dict):
        """Test listing users."""
        # Register second user
        client.post("/api/v1/auth/register", json=test_user_data_2)
        
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/users?skip=0&limit=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_list_users_pagination(self, client: TestClient, registered_user: dict):
        """Test listing users with pagination."""
        headers = {"Authorization": f"Bearer {registered_user['access_token']}"}
        response = client.get("/api/v1/users?skip=0&limit=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
