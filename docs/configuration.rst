Configuration
=============

The Scene Builder is configured per engine and environment, usually in an asset
step and a shot step environment. It must be configured alongside
tk-multi-loader2 and tk-multi-breakdown2 in the same environment.

The app has the following settings:

- ``presets``: the presets the artist can choose from. See
  :ref:`scenebuilder-presets`.
- ``step_dependencies``: the upstream pipeline steps of each pipeline step. See
  :ref:`scenebuilder-step-dependencies`.
- ``best_matching_step_only``: the default state of the **Best matching step
  only** check box. See :ref:`scenebuilder-best-matching-step`.
- ``actions_hook``: the hook called before and after a build. See
  :ref:`scenebuilder-actions-hook`.

.. _scenebuilder-presets:

Presets
-------

A preset has a ``name``, shown in the preset selector of the dialog, and a list
of ``actions``. The first preset is selected when the dialog opens. Each action
has:

- ``context``: a list of Flow Production Tracking filters on the
  ``PublishedFile`` entity, used to find the files to build. Complex filters with
  ``filter_operator`` and ``filters`` are supported.
- ``action_mappings``: a dictionary mapping a Published File Type to the name of
  the Loader action used to load it. Only published files of these types are
  queried. The action names must match the actions configured for the Loader in
  the same environment.

The example below references the files published by the upstream tasks of the
current asset task, using the task dependencies created by a task template.
For a Rig task that depends on a Model task, it lists the latest Model
``Maya Scene`` publish of the asset:

.. code-block:: yaml

    settings.tk-multi-scenebuilder.maya.asset:
      presets:
        - name: Reference
          actions:
            - context:
                - [ entity, is, '{context.entity}' ]
                - [ task.Task.downstream_tasks.Task.content, is, '{context.task.name}' ]
                - [ task.Task.downstream_tasks.Task.step, is, '{context.step}' ]
              action_mappings:
                Maya Scene: reference
        - name: Import
          actions:
            - context:
                - [ entity, is, '{context.entity}' ]
                - [ task.Task.downstream_tasks.Task.content, is, '{context.task.name}' ]
                - [ task.Task.downstream_tasks.Task.step, is, '{context.step}' ]
              action_mappings:
                Maya Scene: import
      location: "@apps.tk-multi-scenebuilder.location"

Context Tokens
______________

Filter values can be one of the following tokens, resolved from the current
context when the dialog loads the preset. A token must be the whole value of the
filter.

======================================  ==============================================
Token                                   Resolves to
======================================  ==============================================
``{context.project}``                   The project entity dictionary
``{context.entity}``                    The entity dictionary, e.g. the Asset or Shot
``{context.step}``                      The pipeline Step entity dictionary
``{context.task}``                      The Task entity dictionary
``{context.<field>.id}``                The ``id`` of one of the entities above
``{context.<field>.name}``              The ``name`` of one of the entities above
``{context.upstream_steps}``            The list of upstream Step codes of the current
                                        step, from ``step_dependencies``
======================================  ==============================================

A filter whose token cannot be resolved matches nothing: for example a filter
on ``{context.task.name}`` when the context has no task, or a filter on
``{context.upstream_steps}`` when the current step has no upstream steps. Such a
filter is removed from the query, taking ``all`` and ``any`` filter groups into
account, and an action whose filters can no longer match anything is skipped
instead of querying Flow Production Tracking. With the ``is_not`` and ``not_in``
operators, such a filter does not restrict anything and is simply dropped.

.. _scenebuilder-step-dependencies:

Step Dependencies
-----------------

Task templates can only link tasks of the same entity, so they cannot express
that a shot's Layout task needs the Rig of the assets in the shot. The
``step_dependencies`` setting fills this gap: it maps the Step code of the
current task to the list of upstream Step codes it pulls published files from.
Use it in a preset filter with the ``{context.upstream_steps}`` token.

The default value is:

.. code-block:: yaml

    step_dependencies:
      Animation: [Rig]
      Layout: [Rig, Texture, Model]

The example below lists the files published on the upstream steps by the
assets linked to the current shot:

.. code-block:: yaml

    settings.tk-multi-scenebuilder.maya.shot:
      presets:
        - name: Upstream Assets
          actions:
            - context:
                - [ entity.Asset.shots, in, '{context.entity}' ]
                - [ task.Task.step.Step.code, in, '{context.upstream_steps}' ]
              action_mappings:
                Maya Scene: reference
      location: "@apps.tk-multi-scenebuilder.location"

.. note:: The ``entity.Asset.shots`` filter only finds assets linked to the shot
    through the Shot's **Assets** field.

Steps that are not listed have no upstream steps, so presets using the token
show no files for them. Configurations can override the setting to match their
own pipeline steps.

The order of each list matters: the first step is the preferred one. It is used
by the **Best matching step only** option, and to sort the files of an entity.

.. _scenebuilder-best-matching-step:

Best Matching Step Only
-----------------------

When an entity has files published on several upstream steps, for example an
asset with both a Rig and a Model, building all of them is rarely what the
artist wants. With the **Best matching step only** check box enabled, the
Scene Builder only shows, for each entity, the files of the first step of the
``step_dependencies`` list that has published files. With the default
``Layout: [Rig, Texture, Model]``, a Layout task shows the Rig of an asset when
there is one, otherwise its Texture, otherwise its Model.

The files of the other steps are hidden and unchecked, so they are not built.
When the artist turns the check box off, they are shown again but stay
unchecked, so it is up to the artist to check the ones to build.

The ``best_matching_step_only`` setting controls the default state of the check
box, ``True`` by default. The check box is disabled when the current step has no
``step_dependencies`` entry.

.. note:: Only files that are not loaded yet are affected. Files that are
    already loaded, out of date or no longer expected are always shown. Files
    are compared within the results of a single preset action, so a preset that
    queries each step in a separate action is not affected.
