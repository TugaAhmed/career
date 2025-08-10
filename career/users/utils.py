# users/utils.py
from django.core import signing
from django.conf import settings
from datetime import timedelta

SIGNER = signing.TimestampSigner()

def make_verification_token(user_id):
    # returns a signed, timestamped token
    return SIGNER.sign(str(user_id))

def verify_token(token, max_age_seconds=3600):
    try:
        unsigned = SIGNER.unsign(token, max_age=max_age_seconds)
        return unsigned  # user id string
    except signing.SignatureExpired:
        return 'expired'
    except signing.BadSignature:
        return None
