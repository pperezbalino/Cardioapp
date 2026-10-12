"""Server-issued pilot access. No billing, API provider or client-selected Pro role."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import os
import re
import secrets
import time


class Feature(str, Enum):
    CALCULATORS = 'calculators'
    CLINICAL_CASE = 'clinical_case'
    PDF = 'pdf'
    MANUAL_ECG = 'manual_ecg'
    AI = 'ai'
    VOICE = 'voice'
    HISTORY = 'history'


PRO_PRICE_USD = '5.99'
ACCESS_LIFETIME_SECONDS = 8 * 60 * 60
_SIGNING_KEY = secrets.token_bytes(32)
_PERMISSIONS = {
    'free': frozenset({Feature.CALCULATORS}),
    'pro': frozenset({Feature.CALCULATORS, Feature.CLINICAL_CASE, Feature.PDF, Feature.MANUAL_ECG}),
}


class AccessDenied(PermissionError):
    pass


@dataclass(frozen=True)
class AccessContext:
    subject: str
    plan: str
    grant: str
    issued_at: float
    signature: str


def _signature(subject, plan, grant, issued_at):
    payload = json.dumps([subject, plan, grant, issued_at], separators=(',', ':')).encode()
    return hmac.new(_SIGNING_KEY, payload, hashlib.sha256).hexdigest()


def _issue(subject, plan, grant, now):
    return AccessContext(subject, plan, grant, now, _signature(subject, plan, grant, now))


def anonymous_access(now=None):
    return _issue('anonymous', 'free', '', time.time() if now is None else now)


def _invitations():
    """Read only server configuration; malformed configuration fails closed."""
    try:
        raw = json.loads(os.environ.get('CARDIOAPP_PRO_INVITES', '{}'))
        if not isinstance(raw, dict):
            return {}
        result = {}
        used_digests = set()
        for subject, record in raw.items():
            if not isinstance(subject, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', subject) or not isinstance(record, dict):
                return {}
            digest = record.get('sha256')
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                return {}
            if digest in used_digests:
                return {}
            used_digests.add(digest)
            expiry = record.get('expires_at')
            if expiry:
                expiration = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                if expiration.tzinfo is None:
                    return {}
                expiry = expiration.timestamp()
            result[subject] = {'sha256': digest, 'expires_at': expiry}
        return result
    except (ValueError, TypeError, AttributeError):
        return {}


def pilot_access(code, now=None):
    now = time.time() if now is None else now
    if not isinstance(code, str) or not 24 <= len(code) <= 200:
        raise AccessDenied('invalid_invitation')
    digest = hashlib.sha256(code.encode()).hexdigest()
    for subject, invitation in _invitations().items():
        if hmac.compare_digest(digest, invitation['sha256']):
            if invitation['expires_at'] and now >= invitation['expires_at']:
                break
            return _issue(subject, 'pro', digest, now)
    raise AccessDenied('invalid_invitation')


def valid_access(context, now=None):
    now = time.time() if now is None else now
    if not isinstance(context, AccessContext) or context.plan not in _PERMISSIONS:
        return False
    try:
        if not hmac.compare_digest(context.signature, _signature(context.subject, context.plan,
                                                               context.grant, context.issued_at)):
            return False
        if not 0 <= now - context.issued_at < ACCESS_LIFETIME_SECONDS:
            return False
        if context.plan == 'pro':
            invitation = _invitations().get(context.subject)
            return bool(invitation and hmac.compare_digest(invitation['sha256'], context.grant)
                        and (not invitation['expires_at'] or now < invitation['expires_at']))
        return context.subject == 'anonymous' and context.grant == ''
    except (TypeError, ValueError):
        return False


def allows(context, feature):
    return valid_access(context) and feature in _PERMISSIONS[context.plan]


def require(context, feature):
    if not allows(context, feature):
        raise AccessDenied('pro_required' if feature in _PERMISSIONS['pro'] else 'feature_unavailable')


def current_access():
    import streamlit as st
    context = st.session_state.get('_access_context')
    if not valid_access(context):
        context = anonymous_access()
        st.session_state['_access_context'] = context
    return context
