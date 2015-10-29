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
import os
import logging

from clis import clis

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def run():
    loop = asyncio.get_event_loop()
    default_key = os.path.expanduser("~/.ssh/id_rsa.pub")
    s = clis.Server(loop, ssh_keys=[default_key])
    loop.run_until_complete(s.start())
    LOG.info("Entering event loop")
    loop.run_forever()
