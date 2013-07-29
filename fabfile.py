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


def expand_config(env):
    #  system user, owner of the processes and code on your server
    #  the user and it's home dir will be created if not present
    env.runner_user = 'www-data'
    # user group
    env.runner_group = env.runner_user
    #  the code of your project will be located here
    env.deploy_root = join('/srv', 'www')
    #  projects path
    env.projects_path = join(env.deploy_root, env.project)
    #  the root path of your project
    env.code_root = join(env.projects_path, 'src')

    env.django_enabled = False
    #  the Python path to a Django settings module.
    env.django_project_settings = 'cgt/settings.py'
    #  django media dir
    env.django_media_path = join(env.code_root, 'static/media')
    #  django static dir
    env.django_static_path = join(env.code_root, 'static')
    #  django media url and root dir
    env.django_media_url = '/media/'
    env.django_media_root = env.code_root
    #  django static url and root dir
    env.django_static_url = '/static/'
    #  do you use south in your django project?
    env.south_used = False

    #  virtualenv root
    env.virtenv = join(env.deploy_root, 'envs', env.project)
    #  some virtualenv options, must have at least one
    env.virtenv_options = ['distribute', 'no-site-packages', ]
    #  location of your pip requirements file
    #  http://www.pip-installer.org/en/latest/requirements.html#the-requirements-file-format
    #  set it to None to not use
    env.requirements_file = join(env.code_root, 'pip.txt')
    #  always ask user for confirmation when run any tasks
    env.ask_confirmation = True

    ### START gunicorn settings ###
    #  be sure to not have anything running on that port
    env.gunicorn_bind = "127.0.0.1:3000"
    env.gunicorn_logfile = '%(deploy_root)s/logs/%(project)s_gunicorn.log' % env
    env.rungunicorn_script = '%(deploy_root)s/scripts/rungunicorn_%(project)s.sh' % env
    env.gunicorn_workers = 1
    env.gunicorn_worker_class = "tornado"
    env.gunicorn_loglevel = "info"
    ### END gunicorn settings ###

    ### START nginx settings ###
    env.nginx_server_name = 'deploy.caigengtan.com'  # Only domain name, without 'www' or 'http://'
    env.nginx_conf_file = '%(deploy_root)s/configs/nginx/%(project)s.conf' % env
    env.nginx_client_max_body_size = 2  # Maximum accepted body size of client request, in MB
    env.nginx_htdocs = '%(deploy_root)s/htdocs' % env
    # will configure nginx with ssl on, your certificate must be installed
    # more info here: http://wiki.nginx.org/HttpSslModule
    env.nginx_https = False
    ### END nginx settings ###

    ### START supervisor settings ###
    # http://supervisord.org/configuration.html#program-x-section-settings
    # default: env.project
    env.supervisor_program_name = env.project
    env.supervisorctl = '/usr/bin/supervisorctl'  # supervisorctl script
    env.supervisor_autostart = 'true'  # true or false
    env.supervisor_autorestart = 'true'  # true or false
    env.supervisor_redirect_stderr = 'true'  # true or false
    env.supervisor_stdout_logfile = '%(deploy_root)s/logs/supervisord_%(project)s.log' % env
    env.supervisord_conf_file = '%(deploy_root)s/configs/supervisord/%(project)s.conf' % env
    ### END supervisor settings ###
