# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Services."""


from .config import MemberServiceConfig
from .service import MemberService


__all__ = (
    'MemberService',
    'MemberServiceConfig',
)
