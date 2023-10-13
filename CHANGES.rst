..
    This file is part of Invenio.
    Copyright (C) 2016-2023 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Changes
=======

Version 7.15.2 (released 2023-10-13)

- ui: allow trailing slashes

Version 7.15.1 (released 2023-10-11)

- community: fix deletion modal fields UI

Version 7.15.0 (released 2023-10-10)

- header: add manage community button

Version 7.14.0 (released 2023-10-04)

- default community: add possibility to set to None
- searchapp: reduce the pagination options to 10 and 20

Version 7.13.1 (released 2023-10-02)

- communities: replace lru_cache with invenio_cache to ensure that cache expiration
  using a TTL is correctly handled

Version 7.13.0 (released 2023-10-02)

- notifications: add notifications on invitation actions
- settings menu: rename curation policy menu item to review policy
- settings: remove hidden divider from pages

Version 7.12.1 (released 2023-09-28)
------------------------------------

- fix service utility to cache community's slug

Version 7.12.0 (released 2023-09-28)
------------------------------------

- add service utility to cache community's slug
- service: fix sort param modifying sort options variable
- community settings: toggle danger zone area based on permissions

Version 7.11.0 (released 2023-09-25)
------------------------------------

- services: add community deletion
- moderation: delete communities of blocked user
- administration: add community deletion and restore actions
- resource: add revision check on delete header
- ui: add accessibility attributes

Version 7.10.1 (released 2023-09-22)
------------------------------------

- ui: allow redirecting to another page when clicking on
  the community's list item
- fix an issue with wrongly updating users in the db when
  fetching community's members


Version 7.10.0 (released 2023-09-21)
------------------------------------

- resources: add etag headers

Version 7.9.0 (released 2023-09-19)
-----------------------------------

- communities: implement service methods for deletion
- CommunityCompactItem: add external icon and target blank
- communities-profile: fix custom funding form

Version 7.8.0 (released 2023-09-18)
-----------------------------------

- github: drop python 3.7 as it has reached end of life
- communities: add data model for community deletion
- members: remove rendering of HTML for member description
- ui: safely render community `description`
- delete community modal: fix styling

Version 7.7.4 (released 2023-09-14)
-----------------------------------

- installation: bump invenio-vocabularies

Version 7.7.3 (released 2023-09-14)
-----------------------------------

- search bar: add aria-label
- a11y: added ids to TextFields

Version 7.7.2 (released 2023-09-12)
-----------------------------------

- service: exclude created requests from search

Version 7.7.1 (released 2023-09-04)
-----------------------------------

- components: fix visibility permission check on edit


Version 7.7.0 (released 2023-08-30)
-----------------------------------

- oai-pmh: take oai sets prefix from config

Version 7.6.0 (released 2023-08-23)
-----------------------------------

- communities: add `is_verified` field to sort communities based on owner verified status
- user-moderation: implement `on_approve` action to reindex user communities

Version 7.5.0 (released 2023-08-17)
-----------------------------------

- permissions: extract base permissions

Version 7.4.0 (released 2023-08-09)
-----------------------------------

- add user moderation callback hooks
- UI improvements

Version 7.3.0 (released 2023-08-02)
-----------------------------------

- members and invitations: Add invite button to members tab, a11y fixes, UI fixes

Version 7.2.3 (released 2023-07-26)
-----------------------------------

- ui: align search with "My account" header

Version 7.2.2 (released 2023-07-24)
-----------------------------------

- templates: access message and mark subject for translation

Version 7.2.1 (released 2023-07-24)
-----------------------------------

- inject create permissions to communities search

Version 7.2.0 (released 2023-07-21)
-----------------------------------

- notifications: add member invitation notification

Version 7.1.2 (released 2023-07-18)
-----------------------------------

- ui: fix mobile version

Version 7.1.1 (released 2023-07-17)
-----------------------------------

- actions: reorder actions

Version 7.0.1 (released 2023-07-05)
-----------------------------------

- tests: fix users update

Version 7.0.0 (released 2023-06-15)
-----------------------------------

- cache: adds unmanaged groups to be cached and loaded in the identity
- adds identity cache
- add groups as community members
- assets: display metrics on deletion modal

Version 6.7.0 (released 2023-06-07)
-----------------------------------

- notifications: add member recipient generator
- tests: add notification member recipient generator test case
- services: add extra_filter param
- services: provide explicit scan params

Version 6.6.1 (released 2023-06-02)
-----------------------------------

- schemas: use parent class for CommunityGhostSchema stub

Version 6.6.0 (released 2023-05-26)
-----------------------------------

- configure number of items in communities carousel
- add placeholder in communities carousel
- introduce a configuration to disallow the creation of a restricted community
- fix a11y for tabs and modals in communities settings

Version 6.5.0 (released 2023-05-05)
-----------------------------------

- update mappings of members and invitations
- add configurable community permission policy

Version 6.4.0 (released 2023-04-25)
-----------------------------------

- update mappings of members and invitations

Version 6.3.0 (released 2023-04-20)
-----------------------------------

- search: add query parser mappings and allowed terms list
- assets: change import components from invenio-vocabularies and react-invenio-forms

Version 6.2.1 (released 2023-04-06)
-----------------------------------

- improve UX of community deletion modal

Version 6.2.0 (released 2023-04-06)
-----------------------------------

- add custom fields of community to display on about page
- allow blank curation policy page and about page
- add extra filter to community service

Version 6.1.1 (released 2023-03-28)
-----------------------------------

- refactor requests components


Version 6.1.0 (released 2023-03-24)
-----------------------------------

- deny deletion of a community if there are open requests
- add ghost community when the community cannot be resolved


Version 6.0.0 (released 2023-03-20)
-----------------------------------


- upgrade community settings layout
- split pages configuration
- reorganise community details submenu
- reorder details fields
- rename service component configuration variable
- add configurable error handler


Version 5.5.0 (released 2023-03-13)
-----------------------------------


- requests: add community inclusion request tyoe
- rename permission policy for direct publish


Version 5.4.0 (released 2023-03-10)
-----------------------------------

- assets: add abstraction and reusability to search component
- access systemfield: update class attributes tuples into enums
- access systemfield: update validation to a class function
- service: add configurable components

Version 5.3.0 (released 2023-03-10)
-----------------------------------

- Custom fields: add multiple custom field widget loaders
- ui serializer: add permissions
- assets: refactor community components


Version 5.2.0 (released 2023-03-03)
-----------------------------------

- remove deprecated flask_babelex dependency and imports
- upgrade invenio dependencies

Version 5.1.0 (released 2023-02-24)
-----------------------------------

- profile: add about and curation policy tab
- generators: fix permission check for communities on serializers

Version 5.0.1 (released 2023-02-20)
-----------------------------------

- members: add support to read the memberships of an identity (service layer only)

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
