from ISS_TRACKER import get_speed, average_speed
import math
import pytest

##chat GPT helped me with the unit test 
def test_get_speed():
    # Test cases for get_speed function
    assert math.isclose(get_speed(1, 1, 1), math.sqrt(3), rel_tol=1e-6)
    assert math.isclose(get_speed(1, 2, 3), math.sqrt(14), rel_tol=1e-6)
    assert math.isclose(get_speed(1, 0, 0), 1, rel_tol=1e-6)

def test_average_speed():
    # Example data (replace with your actual data)
    data = [
        {'X_DOT': {'#text': '1.0'}, 'Y_DOT': {'#text': '2.0'}, 'Z_DOT': {'#text': '3.0'}},
        {'X_DOT': {'#text': '4.0'}, 'Y_DOT': {'#text': '5.0'}, 'Z_DOT': {'#text': '6.0'}},
    ]

    # Calculate the expected average speed
    expected_average = (get_speed(1.0, 2.0, 3.0) + get_speed(4.0, 5.0, 6.0)) / 2

    # Test the average_speed function
    assert math.isclose(average_speed(data), expected_average, rel_tol=1e-6)

# Run the tests
if __name__ == '__main__':
    pytest.main()