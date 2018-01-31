# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import cui
import os

from cui.tools import processes

from .parser import parse_record, RES_CLS_DONE
from .buffers import ProcessBuffer


cui.def_variable(['cui-gdb', 'gdb-proc'], 'gdb')
cui.def_variable(['cui-gdb', 'processes'], [])

CMD_LIST_SOURCES = 'file-list-exec-source-files'
CMD_LIST_SOURCE = 'file-list-exec-source-file'


def _compress_source_tree(node, node_name=''):
    cui.message('')
    cui.message(str(node) + ' -- ' + str(node_name))
    # Update children recursively
    uncompressed_dirs = node['dirs']
    node['dirs'] = {}
    for child, child_name in map(lambda kv: _compress_source_tree(kv[1], kv[0]),
                                 uncompressed_dirs.items()):
        node['dirs'][child_name] = child

    # Compress this node
    if len(node['files']) == 0 and len(node['dirs']) == 1:
        child_name, child = next(iter(node['dirs'].items()))
        return child, '/'.join([node_name, child_name])
    return node, node_name


def _build_source_tree(files):
    tree = {
        'files': {},
        'dirs': {},
    }

    # Build basic structure
    for source_file in files:
        path = source_file['fullname'].split('/')[1:]
        tree_anchor = tree
        for token in path:
            if token == path[-1]:
                tree_anchor['files'][token] = source_file
            else:
                if token not in tree_anchor['dirs']:
                    tree_anchor['dirs'][token] = {
                        'files': {},
                        'dirs': {},
                    }
                tree_anchor = tree_anchor['dirs'][token]

    # Compress directories with only one node
    return _compress_source_tree(tree)


class GdbProcess(processes.LineBufferedProcess):
    def __init__(self, name):
        super(GdbProcess, self).__init__(
            cui.get_variable(['cui-gdb', 'gdb-proc']),
            '--interpreter=mi',
            name
        )
        self._name = name
        self._command_queue = []
        self._pending_response = '@@init'

    def start(self):
        super(GdbProcess, self).start()
        self.send_command(CMD_LIST_SOURCES)
        self.send_command(CMD_LIST_SOURCE)

    def _send_command_internal(self, command_joined):
        self.send_all('-%s\n' % ' '.join(command_joined))
        self._pending_response = command_joined

    def send_command(self, command, *args):
        command_joined = [command]
        command_joined.extend(args)

        if self._pending_response or self._command_queue:
            self._command_queue.append(command_joined)
            return False

        self._send_command_internal(command_joined)
        return True

    def _send_next_command(self):
        if not self._pending_response and self._command_queue:
            self._send_command_internal(self._command_queue.pop(0))

    def handle_line(self, line):
        if line == '(gdb) ':
            cui.message('Ready ' + str(self._pending_response))
            self._pending_response = None
            self._send_next_command()
        elif line.startswith('~'):
            cui.message('gdb: %s' % line[1:])
        elif line.startswith('^'):
            self.dispatch(*parse_record(line))
        else:
            cui.message('gdb: unknown line %s' % (line))

    def dispatch(self, result_class, results):
        cui.message(str(results))
        if self._pending_response[0] == CMD_LIST_SOURCES:
            cui.message(str(_build_source_tree(results['files'])))

    def db_run(self):
        self.send_command('exec-run')

    def db_continue(self):
        self.send_command('exec-continue')

    def db_break_insert(self, fn):
        self.send_command('break-insert', fn)

    def stop(self):
        self.send_command('gdb-exit')

    def __repr__(self):
        return '%s:%s' % (self._name, self._proc.pid)


# ======================== Completion =========================

complete_processes = cui.complete_from_list(
    lambda: cui.get_variable(['cui-gdb', 'processes'])
)


def read_gdb_process():
    return cui.read_string('Process', complete_fn=complete_processes)


@cui.api_fn
@cui.interactive(lambda: cui.read_file('Image'))
def gdb_start(path):
    proc = GdbProcess(path)
    cui.get_variable(['cui-gdb', 'processes']).append(proc)
    cui.buffer_visible(ProcessBuffer)
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
