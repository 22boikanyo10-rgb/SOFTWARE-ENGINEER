"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestAuthentication:
    """Test suite for authentication endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_register_user_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["is_verified"] is False

    def test_register_user_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration with duplicate email fails."""
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201
        
        # Try to register with same email
        response2 = client.post("/api/v1/auth/register", json=test_user_data)
        assert response2.status_code == 409
        assert "already registered" in response2.json()["detail"]

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email fails."""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_user_weak_password(self, client: TestClient):
        """Test registration with weak password fails."""
        weak_password_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Test successful login."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password"}
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user_data: dict):
        """Test login with wrong password fails."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "WrongPassword123!"}
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_refresh_token_success(self, client: TestClient, registered_user: dict):
        """Test successful token refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"token": registered_user["refresh_token"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token fails."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"token": "invalid-token"}
        )
        assert response.status_code == 401
