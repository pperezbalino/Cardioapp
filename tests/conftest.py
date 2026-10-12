import hashlib
import json
import pytest
from access import pilot_access

TEST_CODE = 'test-only-cardioapp-pro-invite-0001'
OTHER_CODE = 'test-only-cardioapp-pro-invite-0002'


@pytest.fixture(autouse=True)
def pilot_configuration(monkeypatch):
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES', json.dumps({
        'test-doctor': {'sha256': hashlib.sha256(TEST_CODE.encode()).hexdigest()},
        'other-doctor': {'sha256': hashlib.sha256(OTHER_CODE.encode()).hexdigest()},
    }))


@pytest.fixture
def pro_context():
    return pilot_access(TEST_CODE)


@pytest.fixture
def other_context():
    return pilot_access(OTHER_CODE)
