#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Haiming Yin

"""
Payload example
---------------

payload_data = {
  "before" => "5aef35982fb2d34e9d9d4502f6ede1072793222d",
  "repository" => {
    "url" => "http://github.com/defunkt/github",
    "name" => "github",
    "description" => "You're lookin' at it.",
    "watchers" => 5,
    "forks" => 2,
    "private" => 1,
    "owner" => {
      "email" => "chris@ozmm.org",
      "name" => "defunkt"
    }
  },
  "commits" => [
    {
      "id" => "41a212ee83ca127e3c8cf465891ab7216a705f59",
      "url" => "http://github.com/defunkt/github/commit/41a212ee83ca127e3c8cf465891ab7216a705f59",
      "author" => {
        "email" => "chris@ozmm.org",
        "name" => "Chris Wanstrath"
      },
      "message" => "okay i give in",
      "timestamp" => "2008-02-15T14:57:17-08:00",
      "added" => ["filepath.rb"]
    },
    {
      "id" => "de8251ff97ee194a289832576287d6f8ad74e3d0",
      "url" => "http://github.com/defunkt/github/commit/de8251ff97ee194a289832576287d6f8ad74e3d0",
      "author" => {
        "email" => "chris@ozmm.org",
        "name" => "Chris Wanstrath"
      },
      "message" => "update pricing a tad",
      "timestamp" => "2008-02-15T14:36:34-08:00"
    }
  ],
  "after" => "de8251ff97ee194a289832576287d6f8ad74e3d0",
  "ref" => "refs/heads/master"
}
"""

import logging
import os
import subprocess

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

from tornado.options import define, options
from tornado.escape import json_decode

from netaddr import all_matching_cidrs

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


define("port", default=3000, help="run on the given port", type=int)
define("debug", default=False, help="debug mode", type=bool)


# Have to hard coded in source, since github API maybe blocked
# https://api.github.com/meta
GITHUB_META = {
  "hooks": [
    "204.232.175.64/27",
    "192.30.252.0/22"
  ],
  "git": [
    "207.97.227.239/32",
    "192.30.252.0/22"
  ]
}

def valid_remote_ip(remote_ip):
    allowed = GITHUB_META['hooks']
    allowed.append('127.0.0.1')
    matched = all_matching_cidrs(remote_ip, allowed)
    return len(matched) > 0


class GithubWebhookHandler(tornado.web.RequestHandler):

    def post(self):
        if not valid_remote_ip(self.request.remote_ip):
            raise tornado.web.HTTPError(403)

        payload = json_decode(self.get_argument('payload'))

        # hard coded deploy
        repo_name = payload['repository']['name']
        branch = payload['ref'].split('/')[-1]
        script_file = os.path.join(ROOT_DIR, 'deploy.sh')

        if branch == 'master' and repo_name == 'cgt':
            # git pull
            logging.info("Deploy cgt project.")
            pr = subprocess.Popen(
                ['/bin/sh', script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False)

            output, error = pr.communicate()
            if error:
                logging.error(error)
            logging.info(output)


application = tornado.wsgi.WSGIApplication([
    (r"/webhook", GithubWebhookHandler)
])


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    io_loop = tornado.ioloop.IOLoop.instance()
    
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()


if __name__ == "__main__":
    main()
