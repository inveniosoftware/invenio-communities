# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Fake demo records."""

import json
import random


def create_fake_community(faker):
    """Create fake communities for demo purposes."""
    data_to_use = {
        "access": {
            "visibility": random.choice(["public", "restricted"]),
            "member_policy": random.choice(["open", "closed"]),
            "record_policy": random.choice(["open", "closed"]),
        },
        "slug": faker.unique.domain_word(),
        "metadata": {
            "title": faker.sentence(nb_words=5, variable_nb_words=True),
            "description": faker.text(max_nb_chars=250),
            "type": {
                "id": random.choice(["organization", "event", "topic", "project"])
            },
            "curation_policy": faker.text(max_nb_chars=50000),
            "page": faker.text(max_nb_chars=50000),
            "website": "https://" + faker.domain_name(),  # fake.url()
            "organizations": [{"name": "CERN"}],
        },
    }

    return json.loads(json.dumps(data_to_use))
