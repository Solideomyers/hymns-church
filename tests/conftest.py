
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path if not present
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
