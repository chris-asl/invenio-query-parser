# -*- coding: utf-8 -*-
#
# This file is part of Invenio-Query-Parser.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# Invenio-Query-Parser is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-Query-Parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""invenio_query_parser tasks"""

import json

valid_keywords = []


def dotter(d, key, dots):
    """ Given a json schema dictionary (d argument) returns all the properties
        in a dotted notation.

        e.g
        author
        author.full_name
        author.affiliation
        etc...
    """
    if isinstance(d, dict):
        if 'items' in d:
            dots.append(key)
            dotter(d['items'], key, dots)
        elif 'properties' in d:
            dotter(d['properties'], key, dots)
        else:
            for k in d:
                dotter(d[k], key + '.' + k, dots)
    else:
        dots.append(key)
    return dots


def get_dotted_keys(d, key, dots):
    """Removes undesirable information from extracted keywords."""
    dotted_keys = dotter(d, key, dots)
    return set(dotted_key[1:].rsplit('.', 1)[0] for dotted_key in dotted_keys)


def generate_valid_keywords():
    """ Parses all files that contain valid elasticsearch keywords
    and combines them to a list."""
    global valid_keywords
    in_context = True
    try:
        from invenio_base.globals import cfg
        keyword_mapping = cfg['SEARCH_ELASTIC_KEYWORD_MAPPING']
        json_schema_paths = cfg['JSON_SCHEMA_PATHS']
        elastic_config_paths = cfg['ELASTIC_MAPPINGS_PATHS']
        if valid_keywords:
            return valid_keywords
    except (ImportError, RuntimeError):
        in_context = False
        from .config import DEFAULT_KEYWORDS as keyword_mapping
        from .config import JSON_SCHEMA_PATHS as json_schema_paths
        from .config import ELASTIC_MAPPINGS_PATHS as elastic_config_paths
    # Get keywords from configuration file
    keywords = keyword_mapping.keys()
    for k in keyword_mapping.values():
        if isinstance(k, dict):
            keywords += k.keys()
    # Get keywords from the json schema
    for path in json_schema_paths:
        with open(path) as data_file:
            data = json.load(data_file)
        data = data.get('properties')
        dotted_keywords = get_dotted_keys(data, '', [])
        keywords += dotted_keywords
    # Get keywords from elasticsearch mapping
    for path in elastic_config_paths:
        with open(path) as data_file:
            data = json.load(data_file)
        data = data.get('mappings').get('record').get('properties')
        dotted_keywords = get_dotted_keys(data, '', [])
        keywords += dotted_keywords
    if in_context:
        valid_keywords = set(keywords)
        return valid_keywords
    else:
        return set(keywords)
