# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui

from cui.tools import processes

cui.def_variable(['cui-gdb', 'gdb-proc'], 'gdb')
cui.def_variable(['cui-gdb', 'processes'], [])

class GdbProcess(processes.LineBufferedProcess):
    def __init__(self, prog):
        super(GdbProcess, self).__init__(
            cui.get_variable(['cui-gdb', 'gdb-proc']),
            '--interpreter=mi',
            prog
        )
        self._prog = prog

    def handle_line(self, line):
        if line.startswith('~'):
            cui.message('gdb: %s' % line[1:])
        else:
            cui.message('gdb: unknown line %s' % line)

    def __repr__(self):
        return '%s:%s' % (self._prog, self._proc.pid)


class ProcessBuffer(cui.buffers.ListBuffer):
    @classmethod
    def name(cls, **kwargs):
        return "gdb Processes"

    def items(self):
        return cui.get_variable(['cui-gdb', 'processes'])

    def render_item(self, window, item, index):
        return [repr(item)]


@cui.api_fn
@cui.interactive(lambda: cui.read_file('Image'))
def gdb_start(path):
    proc = _Process(path)
    cui.get_variable(['cui-gdb', 'processes']).append(proc)
    cui.buffer_visible(ProcessBuffer)
    proc.start()


def read_gdb_process():
    pass


@cui.api_fn
@cui.interactive(lambda: read_gdb_process(Process))
def gdb_run(path):
    pass
