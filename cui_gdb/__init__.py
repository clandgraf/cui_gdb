# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import cui

from . import buffers
from . import process


cui.def_variable(['cui-gdb', 'gdb-proc'], 'gdb')
cui.def_variable(['cui-gdb', 'processes'], [])


complete_processes = cui.complete_from_list(
    lambda: cui.get_variable(['cui-gdb', 'processes'])
)


def read_gdb_process():
    return cui.read_string('Process', complete_fn=complete_processes)


@cui.api_fn
@cui.interactive(lambda: cui.read_file('Image'))
def gdb_start(path):
    proc = process.GdbProcess(path)
    cui.get_variable(['cui-gdb', 'processes']).append(proc)
    cui.buffer_visible(buffers.ProcessBuffer)
    proc.start()


@cui.api_fn
@cui.interactive(lambda: read_gdb_process(Process))
def gdb_run(proc):
    proc.run()


def gdb_clear_procs():
    for proc in cui.get_variable(['cui-gdb', 'processes']):
        proc.kill(wait=True)


@cui.init_func
def initialize():
    cui.add_exit_handler(gdb_clear_procs)
