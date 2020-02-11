# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
from flask import request
from flask_security import current_user
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors
from marshmallow import ValidationError
from marshmallow import __version_info__ as marshmallow_version


def marshmallow_loader(schema_class):
    """Marshmallow loader for JSON requests."""
    def json_loader():
        request_json = request.get_json()
        context = {}
        pid_data = request.view_args.get('pid_value')
        if pid_data:
            pid, record = pid_data.data
            context['pid'] = pid
            context['record'] = record
        if current_user.is_authenticated:
            context['user_id'] = int(current_user.get_id())
        if marshmallow_version[0] < 3:
            result = schema_class(context=context).load(request_json)
            if result.errors:
                raise MarshmallowErrors(result.errors)
        else:
            # From Marshmallow 3 the errors on .load() are being raised rather
            # than returned. To adjust this change to our flow we catch these
            # errors and reraise them instead.
            try:
                result = schema_class(context=context).load(request_json)
            except ValidationError as error:
                raise MarshmallowErrors(error.messages)

        return result.data
    return json_loader
