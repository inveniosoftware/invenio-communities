# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

import uuid

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, \
    render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import current_user, login_required
from invenio_db import db
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from .forms import CommunityForm, DeleteCommunityForm, EditCommunityForm, \
    SearchForm
from .models import Community, FeaturedCommunity, InclusionRequest
from .utils import Pagination, render_template_to_string, \
    save_and_validate_logo

blueprint = Blueprint(
    'invenio_communities',
    __name__,
    url_prefix='/communities',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/', methods=['GET', ])
def index():
    """Index page with uploader and list of existing depositions."""
    ctx = mycommunities_ctx()

    p = request.args.get('p', type=str)
    so = request.args.get('so', type=str)
    page = request.args.get('page', type=int, default=1)

    so = so or current_app.config.get('COMMUNITIES_DEFAULT_SORTING_OPTION')

    communities = Community.filter_communities(p, so)
    featured_community = FeaturedCommunity.get_featured_or_none()
    form = SearchForm(p=p)
    per_page = 10
    page = max(page, 1)
    p = Pagination(page, per_page, communities.count())

    ctx.update({
        'r_from': max(p.per_page * (p.page - 1), 0),
        'r_to': min(p.per_page * p.page, p.total_count),
        'r_total': p.total_count,
        'pagination': p,
        'form': form,
        'title': _('Communities'),
        'communities': communities.slice(
            per_page * (page - 1), per_page * page).all(),
        'featured_community': featured_community,
    })

    return render_template(
        "invenio_communities/index.html",
        **ctx
    )


@blueprint.app_template_filter('format_item')
def format_item(item, template, name='item'):
    """Render a template to a string with the provided item in context."""
    ctx = {name: item}
    return render_template_to_string(template, **ctx)


@blueprint.app_template_filter('mycommunities_ctx')
def mycommunities_ctx():
    """Helper method for return ctx used by many views."""
    return {
        'mycommunities': Community.query.filter_by(
            id_user=current_user.get_id()
        ).order_by(db.asc(Community.title)).all()
    }


@blueprint.route('/new/', methods=['GET', 'POST'])
@login_required
def new():
    """Create or edit a community."""
    uid = current_user.get_id()
    form = CommunityForm(request.values, csrf_enabled=False)

    ctx = mycommunities_ctx()
    ctx.update({
        'form': form,
        'is_new': True,
        'community': None,
    })

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        data['id'] = data['identifier']
        del data['logo']
        del data['identifier']
        logo_ext = None
        file = request.files.get('logo', None)
        if file:
            logo_ext = save_and_validate_logo(file.stream, file.filename,
                                              data['id'])
            if not logo_ext:
                form.logo.errors.append(
                    _(
                        'Cannot add this file as a logo.'
                        ' Supported formats: png and jpg.'
                        ' Max file size: 1.5MB'
                    )
                )
            else:
                data['logo_ext'] = logo_ext
        if not file or (file and logo_ext):
            c = Community(id_user=uid, **data)
            db.session.add(c)
            db.session.commit()
            flash("Community was successfully created.", category='success')
            return redirect(url_for('.index'))

    return render_template(
        "/invenio_communities/new.html",
        community_form=form,
        **ctx
    )


@blueprint.route('/<string:community_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(community_id):
    """Create or edit a community."""
    # Check existence of community
    u = Community.query.filter_by(id=community_id).first_or_404()

    # Check ownership
    if u.id_user != current_user.id:
        abort(404)

    form = EditCommunityForm(request.values, u, crsf_enabled=False)
    deleteform = DeleteCommunityForm()
    ctx = mycommunities_ctx()
    ctx.update({
        'form': form,
        'is_new': False,
        'community': u,
        'deleteform': deleteform,
    })

    if request.method == 'POST' and form.validate():
        for field, val in form.data.items():
            setattr(u, field, val)
        db.session.commit()
        u.save_collections()
        flash("Community successfully edited.", category='success')
        return redirect(url_for('.edit', community_id=u.id))

    return render_template(
        "invenio_communities/new.html",
        **ctx
    )


@blueprint.route('/<string:community_id>/delete/', methods=['POST'])
@login_required
def delete(community_id):
    """Delete a community."""
    # Check existence of community
    u = Community.query.filter_by(id=community_id).first_or_404()

    # Check ownership
    if u.id_user != current_user.id:
        abort(404)

    deleteform = DeleteCommunityForm(request.values)
    ctx = mycommunities_ctx()
    ctx.update({
        'deleteform': deleteform,
        'is_new': False,
        'community': u,
    })

    if request.method == 'POST' and deleteform.validate():
        db.session.delete(u)
        db.session.commit()
        flash("Community was successfully deleted.", category='success')
        return redirect(url_for('.index'))
    else:
        flash("Community could not be deleted.", category='warning')
        return redirect(url_for('.edit', community_id=u.id))


@blueprint.route('/<string:community_id>/', methods=['GET'])
def detail(community_id=None):
    """Index page with uploader and list of existing depositions."""
    return generic_item(community_id, "invenio_communities/detail.html")


@blueprint.route('/<string:community_id>/search', methods=['GET'])
def search(community_id=None):
    """Index page with uploader and list of existing depositions."""
    return generic_item(community_id, "invenio_communities/search.html")


def generic_item(community_id, template):
    """Index page with uploader and list of existing depositions."""
    # Check existence of community
    u = Community.query.filter_by(id=community_id).first_or_404()
    uid = current_user.get_id()

    ctx = mycommunities_ctx()
    ctx.update({
        'is_owner': u.id_user == uid,
        'community': u,
        'detail': True,
    })

    return render_template(
        template,
        **ctx
    )


@blueprint.route('/<string:community_id>/about/', methods=['GET'])
def about(community_id=None):
    """Index page with uploader and list of existing depositions."""
    # Check existence of community
    u = Community.query.filter_by(id=community_id).first_or_404()
    uid = current_user.get_id()

    ctx = mycommunities_ctx()
    ctx.update({
        'is_owner': u.id_user == uid,
        'community': u,
        'detail': True,
    })

    return render_template(
        "invenio_communities/about.html",
        **ctx
    )


@blueprint.route('/<string:community_id>/curate/', methods=['GET', 'POST'])
@login_required
def curate(community_id):
    """Index page with uploader and list of existing depositions.

    :param community_id: ID of the community to curate.
    """
    # Does community exists
    u = Community.query.filter_by(id=community_id).first_or_404()
    if request.method == 'POST':
        recid = request.json.get('recid', '')  # PID value of type 'recid'
        # 'recid' is mandatory
        if not recid:
            abort(400)

        resolver = Resolver(pid_type='recid',
                            object_type='rec',
                            getter=Record.get_record)
        pid, record = resolver.resolve(recid)  # Resolve recid to a Record

        action = request.json.get('action')
        # Check allowed actions and required permissions
        if action in ['accept', 'reject']:
            if u.id_user != current_user.id:
                abort(403)
        elif action == 'remove':
            if u.id_user != current_user.id:
                abort(403)
        else:  # action not in ['accept', 'reject', 'remove']
            abort(400)

        # Perform actions
        if action == "accept":
            u.accept_record(record)
            return jsonify({'status': 'success'})
        elif action == "reject":
            u.reject_record(record)
            return jsonify({'status': 'success'})
        else:  # action == "remove"
            u.remove_record(record)
            return jsonify({'status': 'success'})

    ctx = {'community': u}
    return render_template('invenio_communities/curate.html', **ctx)


@blueprint.route('/request/', methods=['POST', ])
@login_required
def communityrequest(community_id):
    """Request the inclusion of given record to a community."""
    recid = request.values.get('recid', '', type=uuid.UUID)
    community_id = request.values.get('community_id', '')
    if (not recid) or (not community_id):
        abort(400)
    record = Record.get_record(recid)
    u = Community.query.filter_by(id=community_id).first_or_404()
    if u.id_user != current_user.id:
        abort(403)
    # TODO: Permissions: Who should be able to request for community request ?
    #       Should check for relationship current_user.id -> record.id
    InclusionRequest.create(community=u, record=record)
    return jsonify({'status': 'success'})
