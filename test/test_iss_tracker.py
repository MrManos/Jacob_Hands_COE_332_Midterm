# test_iss_tracker.py

import pytest
from unittest.mock import patch
from iss_tracker import get_data, get_speed 
import requests
import math

## ChatGPT assisted with making these unit tests
@pytest.fixture
def sample_xml_data():
    return b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ndm>
  <oem id="CCSDS_OEM_VERS" version="2.0">
    <body>
      <segment>
        <data>
          <stateVector>
            <EPOCH>2024-045T12:04:00.000Z</EPOCH>
            <X units="km">100.0</X>
            <Y units="km">200.0</Y>
            <Z units="km">300.0</Z>
            <X_DOT units="km/s">1.0</X_DOT>
            <Y_DOT units="km/s">2.0</Y_DOT>
            <Z_DOT units="km/s">3.0</Z_DOT>
          </stateVector>
          <stateVector>
            <EPOCH>2024-045T12:05:00.000Z</EPOCH>
            <X units="km">150.0</X>
            <Y units="km">250.0</Y>
            <Z units="km">350.0</Z>
            <X_DOT units="km/s">1.5</X_DOT>
            <Y_DOT units="km/s">2.5</Y_DOT>
            <Z_DOT units="km/s">3.5</Z_DOT>
          </stateVector>
        </data>
      </segment>
    </body>
  </oem>
</ndm>'''

BASE_URL = 'http://localhost:5000'



def test_get_speed():
    # Test cases for get_speed function
    assert math.isclose(get_speed(1, 1, 1), math.sqrt(3), rel_tol=1e-6)
    assert math.isclose(get_speed(1, 2, 3), math.sqrt(14), rel_tol=1e-6)
    assert math.isclose(get_speed(1, 0, 0), 1, rel_tol=1e-6)
    
    
    
@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

# Test function for the / route
def test_data_route(client):
    # Mock the get_data function to return sample data
    with patch("my_module.get_data") as mock_get_data:
        mock_get_data.return_value = {"root": {"data": "Some data"}}
        response = client.get("/")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == '{"root": {"data": "Some data"}}\n'

    # Test case when iss_data is empty
    with patch("my_module.get_data") as mock_get_data:
        mock_get_data.return_value = {}
        response = client.get("/")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == 'Data has been deleted\n'
        
@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

# Test function for the /epochs route
def test_epochs_route(client):
    # Mock the keys function to return sample data
    with patch("my_module.keys") as mock_keys:
        mock_keys.return_value = [
            {"EPOCH": "2024-045T12:04:00.000Z"},
            {"EPOCH": "2024-045T12:05:00.000Z"},
            # Add more sample data as needed
        ]
        response = client.get("/epochs")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == '["2024-045T12:04:00.000Z","2024-045T12:05:00.000Z"]\n'

    # Test case when iss_data is empty
    with patch("my_module.keys") as mock_keys:
        mock_keys.return_value = []
        response = client.get("/epochs")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == 'Data has been deleted\n'
        
        
        
if __name__ == "__main__":
    pytest.main()