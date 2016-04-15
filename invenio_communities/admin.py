# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Admin model views for Communities."""

from __future__ import absolute_import, print_function

from flask_admin.contrib.sqla import ModelView

from .models import Community, FeaturedCommunity, InclusionRequest


def _(x):
    """Identity function for string extraction."""
    return x


class CommunityModelView(ModelView):
    """ModelView for the Community."""

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    column_display_all_relations = True
    form_columns = ('id', 'owner', 'title', 'description', 'page',
                    'ranking', 'fixed_points')
    column_list = (
        'id',
        'title',
        'owner.id',
        'deleted_at',
        'last_record_accepted',
        'ranking',
        'fixed_points',
    )
    column_searchable_list = ('id', 'title', 'description')


class FeaturedCommunityModelView(ModelView):
    """ModelView for the FeaturedCommunity."""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_display_all_relations = True
    column_list = (
        'community',
        'start_date',
    )


class InclusionRequestModelView(ModelView):
    """ModelView of the InclusionRequest."""

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    column_list = (
        'id_community',
        'id_record',
        'expires_at',
        'id_user'
    )


community_adminview = dict(
    model=Community,
    modelview=CommunityModelView,
    category=_('Communities'),
)

request_adminview = dict(
    model=InclusionRequest,
    modelview=InclusionRequestModelView,
    category=_('Communities'),
)

featured_adminview = dict(
    model=FeaturedCommunity,
    modelview=FeaturedCommunityModelView,
    category=_('Communities'),
)
