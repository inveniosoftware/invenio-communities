{# -*- coding: utf-8 -*-

  This file is part of Invenio.
  Copyright (C) 2016-2020 CERN.

  Invenio is free software; you can redistribute it and/or modify it
  under the terms of the MIT License; see LICENSE file for more details.
#}
Your record: {{ community_record.record["title"] }} been invited to the following community: {{ community_record.community["title"] }}

Click on the following link to respond to the invitation:

{{ record_invitation_link | safe }}
