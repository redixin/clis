# All Rights Reserved.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import asyncio
import argparse
import configparser
import os
import sys
import logging

from clis import clis

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class FilePath:

    def __call__(self, path):
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            raise argparse.ArgumentTypeError("can't open %s" % path)
        return path


def parse_args():
    ap = argparse.ArgumentParser(description="Metadata server for cloud-init")
    ap.add_argument("-c", "--config",
                    help="Configuration file.",
                    type=FilePath())
    ap.add_argument("-k", "--key", action="append",
                    help="Additional ssh public key(s).",
                    type=FilePath())
    return ap.parse_args()


def error(code, message):
    print(message, file=sys.stderr)
    sys.exit(code)


def get_ssh_keys(args):
    keys = []
    config = args.config
    if not config:
        config = os.path.expanduser("~/.clis.ini")
        if not os.path.isfile(config):
            config = None
    if config:
        cfg = configparser.ConfigParser()
        cfg.read(config)
        paths = cfg["DEFAULT"].get("ssh_key_files")
        if paths:
            paths = paths.splitlines()
            for path in paths:
                path = os.path.expanduser(path)
                if not os.path.isfile(path):
                    error(1, "Can't open %s" % path)
                keys.append(path)
    if not keys:
        key = os.path.expanduser("~/.ssh/id_rsa.pub")
        if os.path.isfile(key):
            keys.append(key)
    return list(set(keys + (args.key or [])))


def run():
    args = parse_args()
    ssh_keys = get_ssh_keys(args)
    if not ssh_keys:
        error(2, "Need at lest one ssh key for start")
    LOG.info("Starting with keys %s" % ssh_keys)
    loop = asyncio.get_event_loop()
    s = clis.Server(loop, ssh_keys=ssh_keys)
    loop.run_until_complete(s.start())
    LOG.info("Entering event loop")
    loop.run_forever()
