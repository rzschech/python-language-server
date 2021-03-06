# Copyright 2017 Palantir Technologies, Inc.
import logging
import os
import sys

from rope.base import libutils
from rope.refactor.rename import Rename

from pyls import hookimpl, uris

log = logging.getLogger(__name__)


@hookimpl
def pyls_rename(workspace, document, position, new_name):
    rename = Rename(
        workspace._rope,
        libutils.path_to_resource(workspace._rope, document.path),
        document.offset_at_position(position)
    )

    log.debug("Executing rename of %s to %s", document.word_at_position(position), new_name)
    changeset = rename.get_changes(new_name, in_hierarchy=True, docs=True)
    log.debug("Finished rename: %s", changeset.changes)
    return {
        'documentChanges': [{
            'textDocument': {
                'uri': uris.uri_with(
                    document.uri, path=os.path.join(workspace.root_path, change.resource.path)
                ),
            },
            'edits': [{
                'range': {
                    'start': {'line': 0, 'character': 0},
                    'end': {'line': sys.maxsize, 'character': 0},
                },
                'newText': change.new_contents
            }]
        } for change in changeset.changes]
    }
