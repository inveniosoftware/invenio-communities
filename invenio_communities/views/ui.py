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

import copy
from functools import partial, wraps

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, \
    render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import current_user, login_required
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from invenio_access.models import ActionUsers
from invenio_accounts.models import User
from invenio_communities.forms import CommunityForm, DeleteCommunityForm, \
    EditCommunityForm, SearchForm
from invenio_communities.models import Community, FeaturedCommunity
from invenio_communities.permissions import CommunityCurateActionNeed
from invenio_communities.proxies import current_permission_factory, needs
from invenio_communities.utils import Pagination, render_template_to_string

blueprint = Blueprint(
    'invenio_communities',
    __name__,
    url_prefix='/communities',
    template_folder='../templates',
    static_folder='../static',
)


def _get_needs(action, community=""):
    """
    :param action: the action to execute (i.e. "communities-read")
    :type action: str
    :param community: the community
    :type community: str
    :returns: the need associated with the action
    """
    if community:
        return needs[action](community)
    return needs[action]()


def _get_permission(action, community=""):
    """
    :param action: the action to execute (i.e. "communities-read")
    :type action: str
    :param community: the community
    :type community: str
    :returns: permission the permission associated to this action with
        this community as a parameter
    """
    if community:
        return current_permission_factory[action](community)
    return current_permission_factory[action]()


def pass_community(f):
    """Decorator to pass community."""
    @wraps(f)
    def inner(community_id, *args, **kwargs):
        c = Community.get(community_id)
        if c is None:
            abort(404)
        return f(c, *args, **kwargs)
    return inner


def permission_required(action):
    """Decorator to require permission."""
    def decorator(f):
        @wraps(f)
        def inner(community, *args, **kwargs):
            permission = _get_permission(action, community)
            if not permission.can():
                abort(403)
            return f(community, *args, **kwargs)
        return inner
    return decorator


def permission_required_no_id(action):
    """Decorator to require permission."""
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            permission = _get_permission(action)
            if not permission.can():
                abort(403)
            return f(*args, **kwargs)
        return inner
    return decorator


@blueprint.app_template_filter('format_item')
def format_item(item, template, name='item'):
    """Render a template to a string with the provided item in context."""
    ctx = {name: item}
    return render_template_to_string(template, **ctx)


@blueprint.app_template_filter('mycommunities_ctx')
def mycommunities_ctx():
    """Helper method for return ctx used by many views."""
    communities = Community.filter_communities("", "title").all()
    mycommunities = [c for c in communities if _get_permission("communities-read", c).can()]
    return {
        "mycommunities": mycommunities,
        "permission_create": partial(_get_permission, "communities-create"),
        "permission_curate": partial(_get_permission, "communities-curate"),
        "permission_delete": partial(_get_permission, "communities-delete"),
        "permission_edit": partial(_get_permission, "communities-edit"),
        "permission_read": partial(_get_permission, "communities-read"),
        "permission_team": partial(_get_permission, "communities-team-management")
    }


@blueprint.route('/', methods=['GET', ])
def index():
    """Index page with uploader and list of existing depositions."""
    ctx = mycommunities_ctx()

    p = request.args.get('p', type=str)
    so = request.args.get('so', type=str)
    page = request.args.get('page', type=int, default=1)

    so = so or current_app.config.get('COMMUNITIES_DEFAULT_SORTING_OPTION')

    communities = Community.filter_communities(p, so).all()
    for i, c in enumerate(communities):
        permission = _get_permission("communities-read", c)
        if not permission.can():
            del communities[i]
    featured_community = FeaturedCommunity.get_featured_or_none()
    form = SearchForm(p=p)
    per_page = 10
    page = max(page, 1)
    p = Pagination(page, per_page, len(communities))

    ctx.update({
        'r_from': max(p.per_page * (p.page - 1), 0),
        'r_to': min(p.per_page * p.page, p.total_count),
        'r_total': p.total_count,
        'pagination': p,
        'form': form,
        'title': _('Communities'),
        'communities': communities[per_page * (page - 1):per_page * page],
        'featured_community': featured_community
    })

    return render_template(
        "invenio_communities/index.html",
        **ctx
    )


@blueprint.route('/<string:community_id>/', methods=['GET'])
@pass_community
@permission_required('communities-read')
def detail(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(community, "invenio_communities/detail.html")


@blueprint.route('/<string:community_id>/search', methods=['GET'])
@pass_community
@permission_required('communities-read')
def search(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(
        community,
        current_app.config['COMMUNITIES_SEARCH_TEMPLATE'],
        detail=False)


@blueprint.route('/<string:community_id>/about/', methods=['GET'])
@pass_community
@permission_required('communities-read')
def about(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(community, "invenio_communities/about.html")


def generic_item(community, template, **extra_ctx):
    """Index page with uploader and list of existing depositions."""
    # Check existence of community
    ctx = mycommunities_ctx()
    ctx.update({
        'is_owner': community.id_user == current_user.get_id(),
        'community': community,
        'detail': True,
    })
    ctx.update(extra_ctx)

    return render_template(template, **ctx)


@blueprint.route('/new/', methods=['GET', 'POST'])
@login_required
@permission_required_no_id('communities-create')
def new():
    """Create a new community."""
    form = CommunityForm(request.values)

    ctx = mycommunities_ctx()
    ctx.update({
        'form': form,
        'is_new': True,
        'community': None,
    })

    if form.validate_on_submit():
        data = copy.deepcopy(form.data)

        community_id = data.pop('identifier')
        del data['logo']

        community = Community.create(
            community_id, current_user.get_id(), **data)

        file = request.files.get('logo', None)
        if file:
            if not community.save_logo(file.stream, file.filename):
                form.logo.errors.append(_(
                    'Cannot add this file as a logo. Supported formats: '
                    '  png and jpg. Max file size: 1.5MB.'))
                db.session.rollback()
                community = None

        if community:
            permissions = current_permission_factory.keys()
            permissions.remove("communities-create")
            for permission in permissions:
                db.session.add(ActionUsers(action=permission,
                               user=current_user,
                               argument=community_id))
            db.session.commit()
            flash("Community was successfully created.", category='success')
            return redirect(url_for('.edit', community_id=community.id))

    return render_template(
        "/invenio_communities/new.html",
        community_form=form,
        **ctx
    )


@blueprint.route('/<string:community_id>/edit/', methods=['GET', 'POST'])
@login_required
@pass_community
@permission_required('communities-edit')
def edit(community):
    """Create or edit a community."""
    form = EditCommunityForm(request.values, community)
    deleteform = DeleteCommunityForm()
    ctx = mycommunities_ctx()
    ctx.update({
        'form': form,
        'is_new': False,
        'community': community,
        'deleteform': deleteform,
    })

    if form.validate_on_submit():
        for field, val in form.data.items():
            setattr(community, field, val)

        file = request.files.get('logo', None)
        if file:
            if not community.save_logo(file.stream, file.filename):
                form.logo.errors.append(_(
                    'Cannot add this file as a logo. Supported formats: '
                    '  png and jpg. Max file size: 1.5MB.'))

        if not form.logo.errors:
            db.session.commit()
            flash("Community successfully edited.", category='success')
            return redirect(url_for('.edit', community_id=community.id))

    return render_template(
        "invenio_communities/new.html",
        **ctx
    )


@blueprint.route('/<string:community_id>/delete/', methods=['POST'])
@login_required
@pass_community
@permission_required('communities-delete')
def delete(community):
    """Delete a community."""
    deleteform = DeleteCommunityForm(request.values)
    ctx = mycommunities_ctx()
    ctx.update({
        'deleteform': deleteform,
        'is_new': False,
        'community': community,
    })

    if deleteform.validate_on_submit():
        community.delete()
        db.session.commit()
        flash("Community was deleted.", category='success')
        return redirect(url_for('.index'))
    else:
        flash("Community could not be deleted.", category='warning')
        return redirect(url_for('.edit', community_id=community.id))


@blueprint.route('/<string:community_id>/make-public/', methods=['POST'])
@login_required
@pass_community
@permission_required('communities-edit')
@permission_required('communities-team-management')
def make_public(community):
    """Makes a community public."""
    ActionUsers.query_by_action(
            _get_needs("communities-read", community.id)).delete()
    db.session.commit()
    flash("Community is now public.", category='success')
    return redirect(url_for('.edit', community_id=community.id))


@blueprint.route('/<string:community_id>/curate/', methods=['GET', 'POST'])
@login_required
@pass_community
@permission_required('communities-curate')
def curate(community):
    """Index page with uploader and list of existing depositions.

    :param community_id: ID of the community to curate.
    """
    if request.method == 'POST':
        action = request.json.get('action')
        recid = request.json.get('recid')

        # 'recid' is mandatory
        if not recid:
            abort(400)
        if action not in ['accept', 'reject', 'remove']:
            abort(400)

        # Resolve recid to a Record
        resolver = Resolver(
            pid_type='recid', object_type='rec', getter=Record.get_record)
        pid, record = resolver.resolve(recid)

        # Perform actions
        if action == "accept":
            community.accept_record(record)
        elif action == "reject":
            community.reject_record(record)
        elif action == "remove":
            community.remove_record(record)

        record.commit()
        db.session.commit()
        RecordIndexer().index_by_id(record.id)
        return jsonify({'status': 'success'})

    ctx = {'community': community}
    return render_template(
        current_app.config['COMMUNITIES_CURATE_TEMPLATE'],
        **ctx
    )


@blueprint.route('/<string:community_id>/team/')
@login_required
@pass_community
@permission_required('communities-team-management')
def team_management(community):
    """Team management for communities.

    :param community_id: ID of the community to manage.
    """
    class __action(object):
        def __init__(self):
            self.title = ""
            self.name = ""
            self.existin = []
    
    actions = []
    permissions = current_permission_factory.keys()
    permissions.remove("communities-create")
    permissions.sort()
    for action in permissions:
        a = __action()
        # 12 = len("communities-')
        a.title = action[12:].replace("-", " ").capitalize()
        a.name = action
        a.existing = ActionUsers.query_by_action(
            _get_needs(action, community.id)).all()
        actions.append(a)
    ctx = mycommunities_ctx()
    ctx.update({
        "community": community,
        "actions": actions
    })
    return render_template(
        current_app.config['COMMUNITIES_TEAM_TEMPLATE'],
        **ctx
    )


@blueprint.route('/<string:community_id>/team/delete-user/', methods=['POST'])
@login_required
@pass_community
@permission_required('communities-team-management')
def team_delete_user(community):
    """page to delete a user. redirect to team_management

    :param community_id: ID of the community.
    """
    if not request.method == 'POST':
        abort(404)
    if not "action_id" in request.form:
        flash(u"Error: action not valid.", "danger")
    else:
        action = ActionUsers.query.get(request.form["action_id"])
        if action.argument != community.id:
            flash(u"You don't have the permission for this action.", "danger")
        else:
            db.session.delete(action)
            db.session.commit()
            flash(u"The permission has been succesfully deleted.")
    return redirect(url_for(".team_management", community_id=community.id))


@blueprint.route('/<string:community_id>/team/add/', methods=['GET', 'POST'])
@login_required
@pass_community
@permission_required('communities-team-management')
def team_add(community):
    """Add a member to a team community

    :param community_id: ID of the community to manage.
    """
    actions = current_permission_factory.keys()
    actions.sort()
    default_action = ""
    if "default_action" in request.values:
        default_action = request.values["default_action"]
    ctx = mycommunities_ctx()
    ctx.update({
        "community": community,
        "users": User.query.all(),
        "actions": actions,
        "default_action": default_action
    })
    return render_template(
        current_app.config['COMMUNITIES_TEAM_ADD_TEMPLATE'],
        **ctx
    )


@blueprint.route('/<string:community_id>/team/add-user/', methods=['POST'])
@login_required
@pass_community
@permission_required('communities-team-management')
def team_add_user(community):
    """page to add a user. redirect to team_management

    :param community_id: ID of the community.
    """
    if not request.method == 'POST':
        abort(404)
    if not "action" in request.form or not "user" in request.form:
        flash(u"Error: action not valid.", "danger")
    else:
        user = User.query.get(request.form["user"])
        db.session.add(ActionUsers(action=request.form["action"],
                                   user=user,
                                   argument=community.id))
        db.session.commit()
        flash(u"The permission has been succesfully added.")
    return redirect(url_for(".team_management", community_id=community.id))
