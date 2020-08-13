from __future__ import absolute_import, print_function

import binascii
import os
from base64 import urlsafe_b64encode
from datetime import datetime

from flask import current_app
from itsdangerous import BadData, JSONWebSignatureSerializer, SignatureExpired

SUPPORTED_DIGEST_ALGORITHMS = ('HS256', 'HS512')


class TokenMixin(object):
    """Mix-in class for token serializers."""

    def create_token(self, obj_id, extra_data={}):
        """Create a token referencing the object id with extra data.
        Note random data is added to ensure that no two tokens are identical.
        """
        return self.dumps(
            dict(
                id=obj_id,
                data=extra_data,
                rnd=binascii.hexlify(os.urandom(4)).decode('utf-8')
            )
        )

    def validate_token(self, token, expected_value=None):
        """Validate secret link token.
        :param token: Token value.
        :param expected_value: A dictionary of key/values that must be present
            in the data part of the token (i.e. included via ``extra_data`` in
            ``create_token``).
        """
        try:
            # Load token and remove random data.
            data = self.load_token(token)

            # Compare expected data with data in token.
            if expected_value:
                if expected_value != data["id"]:
                    return None
            return data
        except BadData:
            return None

    def load_token(self, token, force=False):
        """Load data in a token.
        :param token: Token to load.
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        try:
            data = self.loads(token)
        except SignatureExpired as e:
            if not force:
                raise
            data = e.payload

        del data["rnd"]
        return data


class MembershipTokenSerializer(JSONWebSignatureSerializer, TokenMixin):
    """Serializer for email confirmation link tokens.
    Depends upon the secrecy of ``SECRET_KEY``. Tokens expire after a specific
    time (defaults to ``ACCESSREQUESTS_CONFIRMLINK_EXPIRES_IN``). The
    access request id as well as the email address is stored in the token
    together with a random bit to ensure all tokens are unique.
    """

    def __init__(self, expires_in=None, **kwargs):
        """Initialize underlying TimedJSONWebSignatureSerializer."""
        super(MembershipTokenSerializer, self).__init__(
            current_app.config['SECRET_KEY'],
            salt='membershiprequests-email',
            **kwargs
        )

    @classmethod
    def compat_validate_token(cls, *args, **kwargs):
        """Multiple algorithm-compatible token validation."""
        data = None
        for algorithm in SUPPORTED_DIGEST_ALGORITHMS:
            data = cls(algorithm_name=algorithm).validate_token(
                *args, **kwargs)
            if not data:  # move to next algorithm
                continue
        return data
