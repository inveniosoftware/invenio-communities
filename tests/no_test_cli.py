# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Module tests."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner

from invenio_communities.cli import addlogo, init


def test_cli_init(script_info):
    """Test create user CLI."""
    runner = CliRunner()

    # Init a community first time.
    result = runner.invoke(init, obj=script_info)
    assert result.exit_code == 0

    # Init a community when it is already created.
    result = runner.invoke(init, obj=script_info)
    assert 'Bucket with UUID' in result.output_bytes
    assert 'already exists.\n' in result.output_bytes


def test_cli_init(script_info):
    """Test create user CLI."""
    runner = CliRunner()

    # Add logo to an unexisting community.
    result = runner.invoke(addlogo, [
        '00000000-0000-0000-0000-000000000000',
        '',
    ], obj=script_info)
    assert result.exit_code == 0

    # Add logo to an existing community.
