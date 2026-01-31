import pytest
import sys
import os

if __name__ == "__main__":
    os.environ["TESTING"] = "true"
    sys.exit(pytest.main(["-v", "tests/"]))
