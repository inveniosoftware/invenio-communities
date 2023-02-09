..
    This file is part of Invenio.
    Copyright (C) 2016-2021 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Changes
=======

Version 5.0.0 (released 2023-02-09)
-----------------------------------

- datamodel: add new `access.review_policy` subfield
- permisssions: add policy for direct publish

Version 4.1.2 (released 2023-02-07)
-----------------------------------

- a11y: add missing area labels
- detail: fix restricted label in community details page

Version 4.1.1 (released 2023-01-26)
-----------------------------------

- assets: remove namespace from requests overridable ids

Version 4.1.0 (released 2023-01-26)
-----------------------------------

- assets: normalise overridable ids

Version 4.0.7 (released 2023-01-24)
-----------------------------------

- featured: add feature flag for administration panel


Version 4.0.6 (released 2023-01-20)
-----------------------------------

- featured: add tooltip to featured community schema field

Version 4.0.5 (released 2023-01-05)
-----------------------------------

- featured: add overridable id to featured communities component
- assets: refactor eslint warnings
- community: details page styling adjustments

Version 4.0.4 (released 2022-12-05)
-----------------------------------

- permissions: add featured community list action to administration permissions

Version 4.0.3 (released 2022-12-02)
-----------------------------------

- community details search: add search results counter and sort

Version 4.0.2 (released 2022-12-01)
-----------------------------------

- Add identity to links template expand method.
- Add identity to field resolver pick_resolved_fields method.

Version 4.0.1 (released 2022-11-29)
-----------------------------------

- fixtures: add option to feature communities

Version 4.0.0 (released 2022-11-25)
-----------------------------------

- Add links to search results
- Add i18 translations
- Use centralized Axios configuration

Version 3.2.5 (released 2022-11-16)
-----------------------------------

- Ensure members service using bulk indexing in the `rebuild_index` method


Version 3.2.4 (released 2022-11-14)
-----------------------------------

- Added Jinja macro to render featured communities section


Version 3.2.3 (released 2022-11-03)
-----------------------------------

- Add logo to demo data
- Refactor styling


Version 3.2.2 (released 2022-10-26)
-----------------------------------

- Add featured communities carousel component

Version 3.2.1 (released 2022-10-26)
-----------------------------------

- Remove obsolete imports

Version 3.2.0 (released 2022-10-24)
-----------------------------------
- Upgrade invenio-assets
- Upgrade to node v18
- Add responsive classes to community request search
- Fix overflowing content

Version 3.1.0 (released 2022-10-04)
-----------------------------------
- Add OpenSearch v2

Version 3.0.1 (yanked)

Version 3.0.0 (released 2022-09-27)
-----------------------------------
- Drop Elasticsearch < 7
- Add OpenSearch v1

Version 2.8.8 (released 2022-07-12)
-----------------------------------
- Bugfix: display community logo in the header

Version 2.8.7 (released 2022-07-08)
-----------------------------------

- Add multiple destinations search bar
- Search: redesign community search result item
- Invitations: add helptext on member search
- Settings: add file logo size limit
- Add error handling for UUID

Version 2.8.6 (released 2022-07-01)
-----------------------------------
- Requests search: add expanded fields, re-design list view
- Community: update members table, add responsive width for grid columns
- Members: reserve space for success/error icon, clean up table class
- Global: fixes strings marked for translation
- Community header: add community visibility to header
- Dependencies: bump minor version of invenio-requests

Version 2.8.5 (released 2022-06-24)
-----------------------------------
- i18n: fix naming

Version 2.8.4 (released 2022-06-23)
-----------------------------------

- i18n: add german to list of languages
- Homepage: align searchbar and button
- Page subheader: add mobile class

Version 2.8.3 (released 2022-06-21)
-----------------------------------

- Resources: add UI serializer
- i18n: clean up translation strings
- Community logo: add fixed height for pictures
- Settings ui: fix state behaviour
- Members landing page: fix alignment

Version 2.8.2 (released 2022-06-08)
-----------------------------------

- Search bar: fix search event propagation
- UI: remove redundant components
- Members: style action dropdowns
- Global: pin sphinx package
- Global: add black formatter

Version 2.8.1 (released 2022-05-24)

- Rename featured communities section

Version 2.8.0 (released 2022-05-23)


Version 2.3.1 (released 2021-06-10)
-----------------------------------

- Remove invenio dependencies to depend only on rdm-records.


Version 2.3.0 (released 2021-05-28)
-----------------------------------

- Improve visual feedback when changing permissions.
- Align facets with new records-resources faceting paradigm.


Version 2.2.5 (released 2021-04-29)
-----------------------------------

- Initial public release.
