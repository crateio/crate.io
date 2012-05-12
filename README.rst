Crate
=====

Crate is a PyPI_ Mirror/Python Package Index that was written to make it easy to discover
packages, evaluate them for usefulness, and then install them. Additionally it also focuses
on presenting an extremely stable interface to PyPI compatible applications (e.g. pip).

With Crate you should be able to quickly find, evaluate, and install your packages
with no worries about if something is going to be down or not.

Discussion
==========

Discussion about crate can take place either in #crate on freenode or on 
`GitHub Issues <https://github.com/crateio/crate-site/issues>`_.


Technology Stack
================

Crate.io_ is built on top of Python using the Django framework. It uses Celery
to process its shared tasks, PostgreSQL to store its data, and Redis as its
caching layer.

Relation to PyPI
================

The software that powers Crate.io_ defaults to PyPI_, but can technically be used
with any index that presents the same 
`XML-RPC API <http://wiki.python.org/moin/PyPiXmlRpc>`_.

Crate.io_ the website currently only mirrors PyPI_. All packages and their associated
data come from PyPI. Crate.io provides a reliable place for those packages to be stored
and accessed and tries to present a cleaner and more user-friendly interface to
that data.

Development
===========

Install PostgreSQL
------------------

On OS X one possible way is to use `Homebrew
<http://mxcl.github.com/homebrew/>`_::

    brew install postgresql9
    initdb /usr/local/var/postgres9
    mkdir -p ~/Library/LaunchAgents
    cp /usr/local/Cellar/postgresql9/9.0.7/org.postgresql.postgres.plist ~/Library/LaunchAgents/
    launchctl load -w ~/Library/LaunchAgents/org.postgresql.postgres.plist

There are some alternatives to Homebrew for installing PostgreSQL at http://www.postgresql.org/download/

And create the PostgreSQL database::

    createdb crate

For searching packages to work, you will need `elasticsearch
<http://www.elasticsearch.org/>`_. I installed it via Homebrew::

    brew install elasticsearch

Then create and activate a `virtualenv
<https://crate.io/packages/virtualenv/>`_ -- everybody has their favorite way;
here's what I did (``mkvirtualenv`` comes from `virtualenvwrapper
<https://crate.io/packages/virtualenvwrapper/>`_), inspired by `dstufft's gist
<https://gist.github.com/6869afeec3a5ec5ad116>`_::

    mkvirtualenv --no-site-packages --distribute crate-site
    echo "export DJANGO_SETTINGS_MODULE=crateweb.conf.dev.base" >> $VIRTUAL_ENV/bin/postactivate
    echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate
    workon crate-site   # virtualenv is already activated by mkvirtualenv but have to refresh postactivate

Install dependencies::

    pip install -r requirements.txt

Do the Django dance::

    export LC_ALL="en.UTF-8"  # Otherwise I get "TypeError: decode() argument 1 must be string, not None" in django.contrib.auth.management
    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver

Admire the results of your work at http://localhost:8000/::

    open http://localhost:8000/

You won't have any packages in your database which makes testing harder. A full
sync from PyPI takes some time, like 2 days or so the first time but you can
start a full sync and just stop it after 15 minutes or so and you'll have some
packages.

To start downloading packages from `PyPI <http://pypi.python.org/pypi>`_ into
the local database::

    python manage.py celeryd
    python manage.py trigger_bulk_sync

Once you have some packages, then you can build the search index so that you
can search them::

    elasticsearch
    python manage.py rebuild_index

Say yes to blowing away the index since you don't have one yet anyway. Indexing
1073 packages took a few seconds for me.

@@@ Todo Write More Development Docs?

.. _PyPI: http://pypi.python.org/pypi
.. _Crate.io: https://crate.io/
