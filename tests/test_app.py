"""
Tests for the High School Management System API

This test suite uses the AAA (Arrange-Act-Assert) testing pattern
to ensure all endpoints work correctly and handle edge cases.
"""

import pytest
from fastapi.testclient import TestClient
import copy
from src.app import app, activities


@pytest.fixture
def client():
    """Create a TestClient instance for making requests to the app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities database before each test"""
    # Store the original state
    original_activities = copy.deepcopy(activities)
    
    # Yield control to the test
    yield
    
    # Restore the original state after the test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestGetActivitiesEndpoint:
    """Tests for the get activities endpoint"""
    
    def test_get_all_activities(self, client):
        # Arrange
        # (no special setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_structure(self, client):
        # Arrange
        # (no special setup needed)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert f"Signed up {email} for {activity_name}" == result["message"]
        
        # Verify participant was added
        response2 = client.get("/activities")
        assert email in response2.json()[activity_name]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        # Arrange
        activity_name = "NonExistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_enrolled(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipantEndpoint:
    """Tests for the remove participant endpoint"""
    
    def test_remove_existing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        response2 = client.get("/activities")
        assert email not in response2.json()[activity_name]["participants"]
    
    def test_remove_nonexistent_activity(self, client):
        # Arrange
        activity_name = "NonExistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_non_participant(self, client):
        # Arrange
        activity_name = "Basketball Team"  # Empty initially
        email = "notenrolled@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 400
        assert "Participant not found" in response.json()["detail"]
