import pytest

import app


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_current_game():
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    yield
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None