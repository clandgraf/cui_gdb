# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui

from .process import GdbProcess


class _FileHandler(cui.buffers.NodeHandler(is_expanded_=True)):
    def matches(self, item):
        return isinstance(item, tuple) and 'dirs' not in item[1]

    def render(self, window, item, depth, width):
        return [item[0]]


class _DirectoryHandler(cui.buffers.NodeHandler(is_expanded_=True, has_children_=True)):
    def matches(self, item):
        return isinstance(item, tuple) and 'dirs' in item[1]

    def get_children(self, item):
        return list(item[1]['dirs'].items()) + list(item[1]['files'].items())

    def render(self, window, item, depth, width):
        return [item[0]]


class _ProcessHandler(cui.buffers.NodeHandler(is_expanded_=True, has_children_=True)):
    def matches(self, item):
        return isinstance(item, GdbProcess)

    def get_children(self, item):
        return [('Files', item._files)]

    def render(self, window, item, depth, width):
        return [repr(item)]


@cui.buffers.node_handlers(_ProcessHandler, _DirectoryHandler, _FileHandler)
class ProcessBuffer(cui.buffers.DefaultTreeBuffer):
    @classmethod
    def name(cls, **kwargs):
        return "gdb Processes"

    def get_roots(self):
        return cui.get_variable(['cui-gdb', 'processes'])
