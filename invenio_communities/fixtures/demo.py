# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Fake demo records."""

import datetime
import json
import random

from faker import Faker


def create_fake_community():
    """Create fake communities for demo purposes."""

    fake = Faker()
    data_to_use = {
        "access": {
            "visibility": random.choice(["public", "restricted"]),
            "member_policy": random.choice(["open", "closed"]),
            "record_policy": random.choice(["open", "closed", "restricted"])
        },
        "id": fake.domain_word(), # fake id creator ? fake.word() 
        "metadata": {
            "title": fake.sentence(nb_words=5, variable_nb_words=True),
            "description": fake.text(max_nb_chars=2000),
            "type": random.choice(["organization", "event", "topic", "project"]),
            "curation_policy": fake.text(max_nb_chars=2000),
            "page": fake.text(max_nb_chars=2000),
            "website": "https://" + fake.domain_name(), # fake.url()
            "funding":[{
                "funder": {
                    "name": "European Commission",
                    "identifier": "00k4n6c32",
                    "scheme": "ror"
                },
                "award": {
                    "title": "OpenAIRE",
                    "number": "246686",
                    "identifier": ".../246686",
                    "scheme": "openaire"
                }
            }],
            "affiliations": [{
            "name": "CERN",
            "identifiers": [
                {
                "identifier": "01ggx4157",
                "scheme": "ror"
                }
            ]
        }]
        }
    }

    return json.loads(json.dumps(data_to_use))

