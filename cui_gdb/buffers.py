# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui


class ProcessBuffer(cui.buffers.ListBuffer):
    @classmethod
    def name(cls, **kwargs):
        return "gdb Processes"

    def items(self):
        return cui.get_variable(['cui-gdb', 'processes'])

    def render_item(self, window, item, index):
        return [repr(item)]
