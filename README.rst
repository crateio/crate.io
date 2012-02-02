Crate
=====

Crate is a PyPI Mirror/Python Package Index that was written to make it easy to discover
packages, evaluate them for usefulness, and then install them. Additionally it also focuses
on presenting an extremely stable interface to PyPI compatible applications (e.g. pip).

With Crate you should be able to quickly find, evaluate, and install your packages
with no worries about if something is going to be down or not.


Technology Stack
================

Crate.io is built on top of Python using the Django framework. It uses Celery
to process its shared tasks, PostgreSQL to store its data, and Redis as its
caching layer.

Relation to PyPI
================

The software that powers Crate.io defaults to PyPI, but can techincally be used
with any index that presents the same XMLRPC API.

Crate.io the website currently only mirrors PyPI. All Packages and their associated
data come from PyPI. Crate.io provides a reliable place for those packages to be stored
and accessed and tries to present a cleaner and more user-friendly interface to
that data.

Development
===========

@@@ Todo Write Development Docs
