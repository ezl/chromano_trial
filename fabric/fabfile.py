"""
This is the pybrew fabfile. It contains tasks for any pybrew-level
things that we may do to a server. For example, create user accounts
or set up application server.  It assumes the directory structure of
the repo e.g. there is a ssh-keys directory at the same level, etc.
"""

# TODO: Should we automatically ``a2enmod ssl`` in case any hosted site ends up
# needing SSL?

from __future__ import with_statement
from fabric.api import run, put, sudo, env, cd, local, prompt, settings
from fabric.contrib import files
import os
from textwrap import dedent

BASIC_PACKAGES = (
    'man',
    'manpages',
    'aptitude',
    'screen',
    'zsh',
    'subversion',
    'mercurial',
    'git-core',
    'emacs22-nox',
    'emacs-goodies-el',
    'ipython',
    'vim-nox',
    'python-mode',
    'exuberant-ctags',
    'gcc',
    'python-dev',
    'python-virtualenv',
    'python-setuptools',
    'python-pip',
    'language-pack-en',   # so perl will STFU
    'exim4',
    'apticron',           # nag us when there are security updates
    'apt-listchanges',
    'libmysqlclient-dev', # so that mysql plays nice with venvs
    'python-imaging', # because it is hard to install onto virtualenvs
    'sqlite3',
    'python-pysqlite2',
    'python-psycopg2',
)

USERS = {
    'rz' : {'shell':'zsh' },
    'ezl': {'shell':'bash'},
}


def update():
    """
    Updates package list and installs the ones that need updates.
    """
    # Activate Ubuntu's "Universe" repositories.
    files.uncomment('/etc/apt/sources.list', regex=r'deb.*universe',
                    use_sudo=True)
    sudo('apt-get update -y')
    sudo('apt-get upgrade -y')


def basic_setup():
    """
    Updates package list and packages and installs some basic backages
    e.g. svn
    """
    update()
    for pkg in BASIC_PACKAGES:
        sudo('apt-get -y install ' + pkg)
    # in case it can't find the file
    with settings(warn_only=True):
        sudo('mv /etc/apticron/apticron.conf /etc/apticron/apticron.conf.backup')
    put('etc/apticron/apticron.conf', '/etc/apticron/')


def setup_hosts():
    """
    Configure /etc/hosts and /etc/hostname. Make sure that env.host is the
    server's IP address and that env.hostname is the server's hostname.
    """
    if not getattr(env, 'hostname', None):
        print "setup_hosts requires env.hostname. Skipping."
        return None
    ## the following stuff will only be necessary if we need to put entries
    ## like "1.2.3.4 lrz15" into /etc/hosts, but that may not be necessary.
    ## i'll leave the code for now, but i suspect we can delete it.
    ## sanity check: env.host is an IP address, not a hostname
    #import re
    #assert(re.search(r'^(\d{0,3}\.){3}\d{0,3}$', env.host) is not None)
    #files.append("%(host)s\t%(hostname)s" % env, '/etc/hosts', use_sudo=True)
    files.append("127.0.1.1\t%s" % env.hostname, '/etc/hosts', use_sudo=True)
    sudo("hostname %s" % env.hostname)
    sudo('echo "%s" > /etc/hostname' % env.hostname)


def make_users():
    """
    Creates an admin group and users for rz, ccg, s in that group. The
    users can't login (no password) run the init_users action instead.
    """
    sudo('groupadd admin')
    for u,s in USERS.iteritems():
        sudo('useradd -G admin -m -s `which %s` %s' % (s['shell'], u))


def set_ssh_keys(target_user=None):
    """
    Grabs the ssh-keys from ssh-keys and concats each user's keys into
    his ~/.ssh/authorized_keys. Note that it assumes the users already
    exist. Use it to update the ssh-keys. If you are trying to create
    users from scratch use init_users instead.

    If the target_user argument is present, the ssh keys will be added
    to that user's authorized keys.
    """
    local('tar czf ssh-keys.tar.gz ssh-keys')
    put('ssh-keys.tar.gz', 'ssh-keys.tar.gz')
    local('rm -f ssh-keys.tar.gz')
    sudo('tar xzf ssh-keys.tar.gz')
    for u in USERS.iterkeys():
        target_u = target_user if target_user else u
        sudo('mkdir -p /home/%s/.ssh' % target_u)
        sudo('cat ssh-keys/%s/* >> /home/%s/.ssh/authorized_keys' % (u,target_u))
        sudo('chown -R %s:%s /home/%s/.ssh' % ((target_u,)*3))
    sudo('rm -rf ssh-keys*')


def init_users():
    """
    Makes users and sets their ssh keys. Equivalent to running
    make_users and set_ssh_keys one right after the other.
    """
    make_users()
    set_ssh_keys()


def setup_sudo():
    """
    Copy over the sudoers file that gives the admin group passwordless
    sudo powers.
    """
    put('etc/sudoers', '/etc/sudoers', mode=0440)


def config_sshd():
    """Copies over the sshd_config file (disallows password-based and root
    logins, so make sure init_users has been run before this) and restarts
    the ssh daemon"""
    put('etc/ssh/sshd_config', '/etc/ssh/sshd_config')
    sudo('chmod 0644 /etc/ssh/sshd_config')
    sudo('/etc/init.d/ssh restart')


def all():
    """
    Installs basic packages, gives everyone in USERS user accounts,
    configures sudo and ssh
    """
    basic_setup()
    setup_hosts()
    init_users()
    setup_sudo()
    config_sshd()
    install_apache()
    install_postgres()


def install_apache():
    pkgs = ('apache2', 'apache2-utils', 'libapache2-mod-wsgi', )
    for pkg in pkgs:
        sudo('apt-get -y install %s' % pkg)
    sudo('virtualenv --no-site-packages /var/www/virtualenv')
    sudo('echo "WSGIPythonHome /var/www/virtualenv" >> /etc/apache2/conf.d/wsgi\
-virtualenv')
    sudo('a2enmod ssl')
    files.append('ServerName localhost', '/etc/apache2/httpd.conf',
                 use_sudo=True)
    sudo('/etc/init.d/apache2 reload')


def apache_reload():
    """
    Do a graceful restart of Apache. Reloads the configuration files and the
    client app code without severing any active connections.
    """
    sudo('/etc/init.d/apache2 reload')


def apache_restart():
    """
    Restarts Apache2. Only use this command if you're modifying Apache itself
    in some way, such as installing a new module. Otherwise, use apache reload
    to do a graceful restart.
    """
    sudo('/etc/init.d/apache2 restart')


def setup_xsendfile():
    # TODO: use a secure, temporary, remote directory in case somebody else
    # is screwing around with files named mod_xsendfile.* in /tmp/
    """
    Setup support in Apache for the XSendFile extension to support large,
    downloadable files.
    """
    with cd('/tmp/'):
        # Make sure apxs2, the apache extension tool, is installed:
        sudo('apt-get install -y apache2-threaded-dev')
        # Download, compile, and install mod_xsendfile:
        sudo('wget http://tn123.ath.cx/mod_xsendfile/mod_xsendfile.c')
        with settings(warn_only=True):
            sudo('apxs2 -cia mod_xsendfile.c')
            print(dedent("""\n
                    NOTE: apxs2 is buggy. If you put the LoadModule
                    directive in a separate file in /etc/apache2/conf.d/, then
                    it generates an error about a missing directive in
                    httpd.conf. But if you put the LoadModule directive in
                    httpd.conf, then it puts in a second, duplicate directive
                    that generates a different error. Either way, it generates
                    an error that causes this script to abort. So I'm
                    putting the LoadModule directive into a separate file in
                    conf.d, because that's the cleaner, Ubuntu-standard way to
                    do it, and I'm disabling warnings for this command. Please
                    look carefully and make sure there was no genuine error
                    during complication or installation.\n\n"""))
        files.append('LoadModule xsendfile_module /usr/lib/apache2/modules/mod_xsendfile.so',
                     '/etc/apache2/conf.d/mod_xsendfile', use_sudo=True)
        sudo('rm mod_xsendfile.*')
        sudo('/etc/init.d/apache2 restart')


def install_postgres():
    pkgs = ('postgresql', 'python-egenix-mxdatetime')
    for pkg in pkgs:
        sudo('apt-get -y install %s' % pkg)
    sudo('apt-get -y install postgresql')
    sudo('apt-get -y build-dep psycopg2')


def setup_project_user(project_name):
    """
    Create a user and SSH key for the project.
    """
    sudo('adduser --ingroup www-data --gecos %s --disabled-password %s)' % ((project_name,)*2))
    set_ssh_keys(target_user=project_name)
    # save the env.user, but run the remaining commands as the project_name user we just created
    with settings(user=project_name):
        with cd('/home/%s' % project_name):
            run('mkdir -p .ssh')
            run('ssh-keygen -t rsa -f .ssh/id_rsa -N ""')
            # TODO: fix this so that it is not python version dependent?
            #run('ln -s /usr/lib/python2.5/site-packages/PIL env/lib/python2.6/site-packages/')
            # so that we don't get a yes/no prompt when checking out codebase repos
            files.append('Host codebasehq.com\n    StrictHostKeyChecking no\n',
                         '.ssh/config')
            run('mkdir log')
            print("Here is the project user's public key:")
            run('cat .ssh/id_rsa.pub')
            print("Go the the project settings page on codebase and")
            print("  add that public key as a deploy key.")
            print("You may need to wait a few moments for the key to become active.")
            print("If you are running the `setup_project` command,")
            print("  this script will attempt a `git clone` next.")
    # TODO: put ssh key into deployment keys on codebase via API
    # in the meantime, prompt user to go do it and hit any key to continue
    prompt("Press enter to continue.")


def setup_project_virtualenv(project_name, site_packages=False):
    """
    Create a clean virtualenv for a project in its home directory.
    """
    with settings(user=project_name):
        with cd('/home/%s' % project_name):
            # TODO: if env/ exists, make a backup of it first?
            run('rm -rf env')
            run('virtualenv %s env' % ('' if site_packages else '--no-site-packages' ))
            run('env/bin/easy_install -U setuptools')
            run('env/bin/easy_install pip')
            run('env/bin/pip install -r %s/deploy/requirements.txt' %
                project_name)


def setup_project_code(project_name, git_url, site_packages=False):
    """
    Check out the project's code into its home directory.
    """
    with cd('/home/%s' % project_name):
        with settings(user=project_name):
            run('git clone %s %s' % (git_url, project_name))
            # TODO: test this to make sure it works on projects that have
            # no submodules
            with cd('%s' % project_name):
                #run('git submodule update --init') # --recursive')
                run('git submodule init')
                run('git submodule update')


def setup_project(project_name, git_url, site_packages=False):
    """
    Do a full deploy of a project to a server. Assumes that the app has never
    been deployed on that server before and does all the setup, including
    creating a user account, setting up a virtualenv, and deploying the code.
    """
    setup_project_user(project_name)
    setup_project_code(project_name, git_url, site_packages)
    setup_project_virtualenv(project_name, site_packages)
    with cd('/home/%s' % project_name):
        # permissions for media/
        sudo('chgrp www-data -R %s/media/' % project_name)
        sudo('chmod g+w %s/media/' % project_name)
        # apache config
        sudo('ln -s $PWD/%s/deploy/%s.apache2 /etc/apache2/sites-available/' %
             ((project_name, )*2))
        sudo('a2ensite %s.apache2' % project_name)
    apache_reload()


def update_project(project_name):
    """
    Pull in the latest source to a deployed project.
    """
    with cd('/home/%s/%s' % (project_name, project_name)):
        with settings(user=project_name):
            run('git pull origin master')
            run('git submodule update') # --init') # --recursive')
            run('touch deploy/%s.wsgi' % project_name)


def sqlite_syncdb(project_name):
    """
    Does syncdb and sets permissions for read-write SQLite3.
    Only required in the case where apache is running as a different user
    from the project's user.
    """
    d = {'proj': project_name}
    # Note that if you have initial_data.* fixtures at the top-level of the
    # project, they won't get loaded unless you run manage.py from the same
    # directory. That's why this script is cd'ing all the way into the git
    # repo.
    sqlite_file = '/home/%(proj)s/%(proj)s/production.sqlite3' % d
    with cd('/home/%(proj)s/%(proj)s' % d):
        with settings(user=project_name):
            run('../env/bin/python manage.py syncdb --noinput --settings=production-settings')
            run('chmod g+w ' + sqlite_file)
        sudo('chgrp -R www-data .')
        sudo('chmod g+w .')


def sqlite_resetdb(project_name):
    """
    Deletes the SQLite3 file and runs sqlite_syncdb to recreate it.
    """
    # FIXME: DRY!
    d = {'proj': project_name}
    sqlite_file = '/home/%(proj)s/%(proj)s/production.sqlite3' % d
    with settings(warn_only=True):
        sudo('rm ' + sqlite_file)
    sqlite_syncdb(project_name)


def add_app_to_postgres(project_name, app_server_ip):
    """
    Fake command. UNTESTED. Placeholder/remind of postgres commands.

    Create a database called ``project_name`` owned by a postgres user also
    called ``project_name``.
    """
    d = {'proj': project_name, 'app_ip': app_server_ip}
    with settings(user='postgres'):
        run('createuser %(proj)s -U postgres -E -P %(proj)s' % d)
        # Need to deal with all this interactive user entry...
        # TODO: check if all these things have command-line equivalents:
        # Enter password for new role:
        # Enter it again:
        # Shall the new role be a superuser? (y/n) n
        # Shall the new role be allowed to create databases? (y/n) y
        # Shall the new role be allowed to create more new roles? (y/n) n
        run('createdb -U postgres -O %(proj)s -E UTF8 %(proj)s' % d)
        files.append("host %(proj)s %(proj)s %(app_ip)s md5" % d,
                     '/etc/postgresql/8.3/main/pg_hba.conf', use_sudo=True)
    sudo('/etc/init.d/postgresql-8.3 reload')
    # NOTE: psycopg2 depends on egenix-mx-datetime, which won't install with
    # pip on ubuntu. it'll only install with easy_install with a special link:
    # easy_install -i http://downloads.egenix.com/python/index/ucs4/ egenix-mx-base
    # actually, somehow it works on rodrigo workstation but fails on lrz3, so
    # it's *possible* to get it to work inside pip, but we haven't figure out
    # what the difference is yet.


# "hosts" commands/shortcuts for our servers
def qslinode(user=None):
    env.hosts = ['72.14.181.111']
    env.hostname = 'qslinode'
    if user:
        env.user = user

def who():
    """
    Prints the current USERs list.
    """
    for k,v in USERS.items():
        print k,v
