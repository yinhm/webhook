#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path[0:0] = ['../django-fagungis']

from os.path import join
from fabric.api import env, task
from fagungis.tasks import *


@task
def webhook():
    env.user = 'root'

    #  name of your project - no spaces, no special chars
    env.project = 'webhook'
    #  hg repository of your project
    env.repository = 'git@github.com:yinhm/webhook.git'
    #  type of repository (git or hg)
    env.repository_type = 'git'
    #  hosts to deploy your project, users must be sudoers
    env.hosts = ['stage', ]
    # additional packages to be installed on the server
    env.additional_packages = [
        #'mercurial',
    ]

    expand_config(env)

    # default to root user for deployment,
    # may need to change to a sudo user to enhance security.
    env.runner_user = 'root'
    env.runner_group = 'root'

    env.gunicorn_bind = "127.0.0.1:3000"
    env.gunicorn_workers = 1
    env.gunicorn_worker_class = "tornado"
    env.gunicorn_loglevel = "debug"

    env.nginx_server_name = 'deploy.caigengtan.com'
    env.nginx_client_max_body_size = 2

