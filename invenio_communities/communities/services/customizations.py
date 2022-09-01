# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""

from invenio_base.utils import load_or_import_from_config

from ..searchconfig import SearchConfig


#
# Helpers
#
def _make_cls(cls, attrs):
    """Make the custom config class."""
    return type(
        f"Custom{cls.__name__}",
        (cls,),
        attrs,
    )


#
# Mixins
#
class SearchOptionsMixin:
    """Customization of search options."""

    @classmethod
    def customize(cls, opts):
        """Customize the search options."""
        attrs = {}
        if opts.facets:
            attrs["facets"] = opts.facets
        if opts.sort_options:
            attrs["sort_options"] = opts.sort_options
            attrs["sort_default"] = opts.sort_default
            attrs["sort_default_no_query"] = opts.sort_default_no_query

        return _make_cls(cls, attrs) if attrs else cls


class FromConfigSearchOptions:
    """Data descriptor for search options configuration."""

    def __init__(self, config_key, default=None, search_option_cls=None):
        """Constructor for data descriptor."""
        self.config_key = config_key
        self.default = default or {}
        self.search_option_cls = search_option_cls

    def __get__(self, obj, objtype=None):
        """Return value that was grafted on obj (descriptor protocol)."""
        search_opts = obj._app.config.get(self.config_key, self.default)
        sort_opts = obj._app.config.get("COMMUNITIES_SORT_OPTIONS")
        facet_opts = obj._app.config.get("COMMUNITIES_FACETS")

        search_config = SearchConfig(
            search_opts,
            sort=sort_opts,
            facets=facet_opts,
        )

        return self.search_option_cls.customize(search_config)


class ConfiguratorMixin:
    """Shared customization for requests service config."""

    @classmethod
    def build(cls, app):
        """Build the config object."""
        return type(f"Custom{cls.__name__}", (cls,), {"_app": app})()
