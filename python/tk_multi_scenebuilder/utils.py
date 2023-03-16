# Copyright (c) 2021 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.util import sgre as re

REGEX_PATTERN = r"{context.(\w+)(.(\w+))*}"
ENTITY_LIST = ["project", "entity", "step", "task"]
FIELD_LIST = ["id", "name"]


def resolve_filters(filters):
    """
    When passed a list of filters, it will resolve strings found in the filters using the context.
    For example: '{context.user}' could get resolved to {'type': 'HumanUser', 'id': 86, 'name': 'Philip Scadding'}

    :param filters: A list of filters that has usually be defined by the user or by default in the environment yml
    config or the app's info.yml. Supports complex filters as well. Filters should be passed in the following format:
    [[task_assignees, is, '{context.user}'],[sg_status_list, not_in, [fin,omt]]]

    :return: A List of filters for use with the shotgun api
    """
    app = sgtk.platform.current_bundle()

    resolved_filters = []
    for filter in filters:
        if type(filter) is dict:
            resolved_filter = {
                "filter_operator": filter["filter_operator"],
                "filters": resolve_filters(filter["filters"]),
            }
        else:
            resolved_filter = []
            for field in filter:
                m = re.match(REGEX_PATTERN, field)
                if m:
                    if m.group(1) in ENTITY_LIST:
                        if not m.group(3):
                            field = getattr(app.context, m.group(1))
                        elif m.group(3) and m.group(3) in FIELD_LIST:
                            field = getattr(app.context, m.group(1), {}).get(m.group(3))
                resolved_filter.append(field)
        resolved_filters.append(resolved_filter)
    return resolved_filters
