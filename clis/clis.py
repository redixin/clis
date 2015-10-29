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
import uuid

import yaml
import json
from aiohttp import web

LOG = logging.getLogger(__name__)


class AWS:
    """AWS

    layout:
        /2009-04-04/meta-data/instance-id
    """

    def __init__(self, server):
        self.server = server

    def instance_id(self, request):
        return web.Response(body=b"wat")

    def meta_data(self, request):
        return web.Response(body=b"wat")

    def user_data(self, request):
        return web.Response(body=b"wat")

    def handler(self, request):
        path = request.match_info["path"]
        LOG.info("PATH %s" % path)
        if path == "instance-id":
            return self.instance_id(request)
        if path == "user-data":
            return self.user_data(request)
        if path == "meta-data/":
            return self.meta_data(request)
        return web.Response(body=b"Not found", status=404)

    def index(self, request):
        return web.Response(body=b"Not found", status=404)


class OpenStack:
    """OpenStack datasource.

    layout:
        /openstack/2012-08-10/user_data
        /openstack/2012-08-10/meta_data.json
        /openstack/latest/ -- alias for 2012-08-10
    """

    def __init__(self, server):
        self.server = server

    def get_metadata(self, request):
        remote_host = request.transport.get_extra_info("peername")[0]
        LOG.info("Metadata request from %s" % remote_host)
        keys = {}
        for i, key in enumerate(self.server.ssh_public_keys):
            keys["key-" + str(i)] = key
        return json.dumps({
                "uuid": str(uuid.uuid4()),
                "availability_zone": "nova",
                "hostname": "vm-%s" % remote_host.replace(".", "-"),
                "launch_index": 0,
                "meta": {
                    "priority": "low",
                    "role": "vm-on-localhost",
                },
                "public_keys": keys,
                "name": "test"
        }).encode("utf8")

    def user_data(self, request):
        version = request.match_info["version"]
        if version not in ("2012-08-10", "latest"):
            return web.Response(body=b"Not found", status=404)
        return web.Response(body=self.server.user_data)

    def meta_data(self, request):
        version = request.match_info["version"]
        if version not in ("2012-08-10", "latest"):
            return web.Response(body=b"Not found", status=404)
        return web.Response(body=self.get_metadata(request),
                            content_type="application/json")

    @asyncio.coroutine
    def handler(self, request):
        if request.match_info["version"] not in ("2012-08-10", "latest"):
            return web.Response(b"Not found\n", status=404)
        path = request.match_info["path"]
        if path == "meta_data.json":
            return self.meta_data(request)
        if path == "user_data":
            return self.user_data(request)
        if path == "":
            return web.Response(body=b"user_data\nmeta_data.json")
        return web.Response(body=b"Not found", status=404)

    @asyncio.coroutine
    def index(self, request):
        return web.Response(body=b"2012-08-10/\nlatest")


class Server:
    """Metadata server for cloud-init."""

    def __init__(self, loop, **config):
        self.loop = loop
        self.config = config

        self.ssh_public_keys = []
        for f in config.get("ssh_keys", []):
            if not os.path.isfile(f):
                continue
            with open(f) as kf:
                for line in kf:
                    if line:
                        self.ssh_public_keys.append(line.strip())
        self.user_data = {
                "manage_etc_hosts": True,
                "ssh_authorized_keys": self.ssh_public_keys,
        }
        self.user_data = b"#cloud-config\n" + yaml.safe_dump(
            self.user_data, default_flow_style=False).encode("utf8")
        self._cache = {}

    @asyncio.coroutine
    def start(self):
        openstack = OpenStack(self)
        aws = AWS(self)
        self.app = web.Application(loop=self.loop)
        r = self.app.router.add_route
        r("GET", "/", self.index)
        r("GET", "/openstack", openstack.index)
        r("GET", "/openstack/", openstack.index)
        r("GET", "/openstack/{version}/{path:.*}", openstack.handler)
        r("GET", "/{version:.+}/{path:.+}", aws.handler)
        r("GET", "/{path:.+}", aws.index)
        self.handler = self.app.make_handler(access_log=LOG)
        addr = self.config.get("listen_addr", "0.0.0.0")
        port = self.config.get("listen_port", 8088)
        self.srv = yield from self.loop.create_server(self.handler, addr, port)
        LOG.info("Metadata server started at %s:%s" % (addr, port))

    @asyncio.coroutine
    def index(self, request):
        return web.Response(body=b"/openstack/")

    @asyncio.coroutine
    def stop(self, timeout=1.0):
        yield from self.handler.finish_connections(timeout)
        self.srv.close()
        yield from self.srv.wait_closed()
        yield from self.app.finish()
