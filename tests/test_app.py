"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store the initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Track and Field": {
            "description": "Sprint, distance, and field event training",
            "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and theatrical productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking and competitive debates",
            "schedule": "Mondays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu", "oliver@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and science fair projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "harper@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    
    # Restore initial state
    activities.update(initial_state)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client, reset_activities):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the get activities endpoint"""

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that get activities returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) > 0

    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities_data = response.json()

        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_known_activities(self, client, reset_activities):
        """Test that known activities are present"""
        response = client.get("/activities")
        activities_data = response.json()

        expected_activities = ["Chess Club", "Soccer Team", "Track and Field", "Art Club"]
        for activity in expected_activities:
            assert activity in activities_data


class TestSignupForActivity:
    """Tests for the signup endpoint"""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        sample_email = "test.student@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert sample_email in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        sample_email = "test.student@mergington.edu"
        # Get initial participants
        response_before = client.get("/activities")
        activities_before = response_before.json()
        chess_participants_before = activities_before["Chess Club"]["participants"].copy()

        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )

        # Check participants after signup
        response_after = client.get("/activities")
        activities_after = response_after.json()
        chess_participants_after = activities_after["Chess Club"]["participants"]

        assert sample_email in chess_participants_after
        assert len(chess_participants_after) == len(chess_participants_before) + 1

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        sample_email = "test.student@mergington.edu"
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        sample_email = "test.student@mergington.edu"
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200

        # Attempt duplicate signup
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]


class TestUnregisterFromActivity:
    """Tests for the unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        sample_email = "test.student@mergington.edu"
        # First sign up
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": sample_email}
        )

        # Then unregister
        response = client.post(
            "/activities/Soccer Team/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert sample_email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        sample_email = "test.student@mergington.edu"
        # Sign up
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": sample_email}
        )

        # Get participants before unregister
        response_before = client.get("/activities")
        activities_before = response_before.json()
        soccer_count_before = len(activities_before["Soccer Team"]["participants"])

        # Unregister
        client.post(
            "/activities/Soccer Team/unregister",
            params={"email": sample_email}
        )

        # Check participants after unregister
        response_after = client.get("/activities")
        activities_after = response_after.json()
        soccer_count_after = len(activities_after["Soccer Team"]["participants"])

        assert sample_email not in activities_after["Soccer Team"]["participants"]
        assert soccer_count_after == soccer_count_before - 1

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        sample_email = "test.student@mergington.edu"
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister when student is not signed up"""
        sample_email = "test.student@mergington.edu"
        response = client.post(
            "/activities/Drama Club/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


class TestActivityParticipantLimits:
    """Tests for activity participant limits"""

    def test_can_signup_when_spots_available(self, client, reset_activities):
        """Test that signup works when spots are available"""
        sample_email = "test.student@mergington.edu"
        response = client.post(
            "/activities/Science Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_participants_list_is_list(self, client, reset_activities):
        """Test that participants list is always a list"""
        response = client.get("/activities")
        activities_data = response.json()

        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_details["participants"], list)
