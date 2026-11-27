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
UPSTREAM_STEPS_TOKEN = "upstream_steps"


def get_upstream_steps():
    """
    Get the upstream pipeline steps of the current context step, as defined in the
    `step_dependencies` app setting.

    :return: A list of Step codes, empty when the current step has no dependencies
    """
    app = sgtk.platform.current_bundle()

    step = app.context.step
    if not step:
        return []
    return list(app.get_setting("step_dependencies").get(step["name"], []))


def prune_empty_list_filters(filters, filter_operator="all"):
    """
    Remove the filters that have an empty list as value, which Flow Production
    Tracking cannot query, e.g. [step.Step.code, in, []].

    Such a filter matches nothing, except with the `is_not` and `not_in` operators,
    where it does not restrict anything. An "all" group matches nothing when any of its filters
    matches nothing, an "any" group only when all of them do.

    :param filters: A list of resolved filters, as returned by `resolve_filters`
    :param filter_operator: How the filters are combined, "all" or "any"
    :return: The pruned list of filters, or None if they cannot match anything
    """
    match_any = filter_operator in ("any", "or")
    pruned = []
    for filter in filters:
        if type(filter) is dict:
            sub_filters = prune_empty_list_filters(
                filter["filters"], filter["filter_operator"]
            )
            if sub_filters:
                pruned.append(
                    {
                        "filter_operator": filter["filter_operator"],
                        "filters": sub_filters,
                    }
                )
                continue
            unrestricted = sub_filters is not None
        elif any(value == [] for value in filter[2:]):
            unrestricted = filter[1] in ("is_not", "not_in")
        else:
            pruned.append(filter)
            continue
        if match_any and unrestricted:
            return []
        if not match_any and not unrestricted:
            return None
    if match_any and not pruned:
        return None
    return pruned


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
                m = re.match(REGEX_PATTERN, field) if isinstance(field, str) else None
                if m:
                    if m.group(1) == UPSTREAM_STEPS_TOKEN:
                        field = get_upstream_steps()
                    elif m.group(1) in ENTITY_LIST:
                        entity = getattr(app.context, m.group(1))
                        if entity is None:
                            # An empty list makes the filter unmatchable, see
                            # prune_empty_list_filters.
                            field = []
                        elif not m.group(3):
                            field = entity
                        elif m.group(3) in FIELD_LIST:
                            field = entity.get(m.group(3))
                resolved_filter.append(field)
        resolved_filters.append(resolved_filter)
    return resolved_filters
