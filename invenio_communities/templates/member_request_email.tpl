{# -*- coding: utf-8 -*-

  This file is part of Invenio.
  Copyright (C) 2016-2020 CERN.

  Invenio is free software; you can redistribute it and/or modify it
  under the terms of the MIT License; see LICENSE file for more details.
#}
The user with email {{ membership_request.user.email }}, has requested to join the community:

{{ community["title"] }}

Click on the following link to respond to the membership request:

{{ invitation_link | safe }}

Please note that above link is only valid for {{ days }} days.
