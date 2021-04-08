# # -*- coding: utf-8 -*-
# #
# # This file is part of Invenio.
# # Copyright (C) 2020 CERN.
# #
# # Invenio is free software; you can redistribute it and/or modify it
# # under the terms of the MIT License; see LICENSE file for more details.

# """Proxy definitions."""

# from __future__ import absolute_import, print_function

# from flask import current_app
# from invenio_rest.errors import RESTException
# from itsdangerous import BadData, JSONWebSignatureSerializer, SignatureExpired


# class InvalidTokenError(RESTException):
#     """Resource access token for invalid token."""

#     code = 400
#     description = 'The token is invalid.'


# def create_token(payload):
#     """Create a token referencing the object id with extra data.

#     Note random data is added to ensure that no two tokens are identical.
#     """
#     jss = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
#     return jss.dumps(payload)


# def validate_token(token, expected_value=None):
#     """Validate secret link token.

#     :param token: Token value.
#     :param expected_value: A dictionary of key/values that must be present
#         in the data part of the token (i.e. included via ``extra_data`` in
#         ``create_token``).
#     """
#     try:
#         # Load token and remove random data.
#         data = load_token(token)

#         # Compare expected data with data in token.
#         if expected_value:
#             if expected_value != data:
#                 return None
#         return data
#     except BadData:
#         raise InvalidTokenError()


# def load_token(token, force=False):
#     """Load data in a token.

#     :param token: Token to load.
#     :param force: Load token data even if signature expired.
#                     Default: False.
#     """
#     jss = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

#     try:
#         data = jss.loads(token)
#     except SignatureExpired as e:
#         if not force:
#             raise
#         data = e.payload

#     return data
