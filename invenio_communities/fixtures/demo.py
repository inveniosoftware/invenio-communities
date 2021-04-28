# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Fake demo records."""

import json
import random


def create_fake_community(faker):
    """Create fake communities for demo purposes."""
    data_to_use = {
        "access": {
            "visibility": random.choice(["public", "restricted"]),
            "member_policy": random.choice(["open", "closed"]),
            "record_policy": random.choice(["open", "closed", "restricted"])
        },
        "id": faker.unique.domain_word(),
        "metadata": {
            "title": faker.sentence(nb_words=5, variable_nb_words=True),
            "description": faker.text(max_nb_chars=2000),
            "type": random.choice(
                ["organization", "event", "topic", "project"]),
            "curation_policy": faker.text(max_nb_chars=2000),
            "page": faker.text(max_nb_chars=2000),
            "website": "https://" + faker.domain_name(),  # fake.url()
            "funding": [
                {
                    "funder": {
                        "name": "European Commission",
                        "identifier": "03yrm5c26",
                        "scheme": "ror",
                    },
                    "award": {
                        "title": "OpenAIRE",
                        "number": "246686",
                        "identifier": "0000-0002-1825-0097",
                        "scheme": "orcid",
                    },
                }
            ],
            "organizations": [
                {
                    "name": "CERN",
                    "identifiers": [
                        {"identifier": "01ggx4157", "scheme": "ror"}],
                }
            ],
        },
    }

    return json.loads(json.dumps(data_to_use))
