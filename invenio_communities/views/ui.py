# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

import copy
from functools import wraps

import bleach
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, \
    render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import current_user, login_required
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from invenio_communities.forms import CommunityForm, DeleteCommunityForm, \
    EditCommunityForm, RecaptchaCommunityForm, SearchForm
from invenio_communities.models import Community, FeaturedCommunity
from invenio_communities.proxies import current_permission_factory
from invenio_communities.utils import Pagination, render_template_to_string

blueprint = Blueprint(
    'invenio_communities',
    __name__,
    url_prefix='/communities',
    template_folder='../templates',
    static_folder='../static',
)


@blueprint.app_template_filter('sanitize_html')
def sanitize_html(value):
    """Sanitizes HTML using the bleach library."""
    return bleach.clean(
        value,
        tags=current_app.config['COMMUNITIES_ALLOWED_TAGS'],
        attributes=current_app.config['COMMUNITIES_ALLOWED_ATTRS'],
        strip=True,
    ).strip()


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
            permission = current_permission_factory(community, action=action)
            if not permission.can():
                abort(403)
            return f(community, *args, **kwargs)
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
    return {
        'mycommunities': Community.get_by_user(current_user.get_id()).all()
    }


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
        current_app.config['COMMUNITIES_INDEX_TEMPLATE'], **ctx)


@blueprint.route('/<string:community_id>/', methods=['GET'])
@pass_community
def detail(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(
        community, current_app.config['COMMUNITIES_DETAIL_TEMPLATE'])


@blueprint.route('/<string:community_id>/search', methods=['GET'])
@pass_community
def search(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(
        community,
        current_app.config['COMMUNITIES_SEARCH_TEMPLATE'],
        detail=False)


@blueprint.route('/<string:community_id>/about/', methods=['GET'])
@pass_community
def about(community):
    """Index page with uploader and list of existing depositions."""
    return generic_item(
        community, current_app.config['COMMUNITIES_ABOUT_TEMPLATE'])


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
def new():
    """Create a new community."""
    if current_app.config.get('RECAPTCHA_PUBLIC_KEY') and \
            current_app.config.get('RECAPTCHA_PRIVATE_KEY'):
        form_cls = RecaptchaCommunityForm
    else:
        form_cls = CommunityForm
    form = form_cls(formdata=request.values)

    ctx = mycommunities_ctx()
    ctx.update({
        'form': form,
        'is_new': True,
        'community': None,
    })

    if form.validate_on_submit():
        data = copy.deepcopy(form.data)

        community_id = data.pop('identifier')
        data.pop('recaptcha', None)
        del data['logo']

        community = Community.create(
            community_id, current_user.get_id(), **data)

        file = request.files.get('logo', None)
        if file:
            if not community.save_logo(file.stream, file.filename):
                form.logo.errors.append(_(
                    'Cannot add this file as a logo. Supported formats: '
                    'PNG, JPG and SVG. Max file size: 1.5 MB.'))
                db.session.rollback()
                community = None

        if community:
            db.session.commit()
            flash("Community was successfully created.", category='success')
            return redirect(url_for('.edit', community_id=community.id))

    return render_template(
        current_app.config['COMMUNITIES_NEW_TEMPLATE'],
        community_form=form,
        **ctx
    )


@blueprint.route('/<string:community_id>/edit/', methods=['GET', 'POST'])
@login_required
@pass_community
@permission_required('community-edit')
def edit(community):
    """Create or edit a community."""
    form = EditCommunityForm(formdata=request.values, obj=community)
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
                    'PNG, JPG and SVG. Max file size: 1.5 MB.'))

        if not form.logo.errors:
            db.session.commit()
            flash("Community successfully edited.", category='success')
            return redirect(url_for('.edit', community_id=community.id))

    return render_template(
        current_app.config['COMMUNITIES_EDIT_TEMPLATE'],
        **ctx
    )


@blueprint.route('/<string:community_id>/delete/', methods=['POST'])
@login_required
@pass_community
@permission_required('community-delete')
def delete(community):
    """Delete a community."""
    deleteform = DeleteCommunityForm(formdata=request.values)
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


@blueprint.route('/<string:community_id>/curate/', methods=['GET', 'POST'])
@login_required
@pass_community
@permission_required('community-curate')
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
