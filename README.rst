Overview
========

**django-failclose** aims to provide the option to make Django a failclose system.
That means that instead of giving free access to every view by default and
then restricting it on a case by case basis, access to all views will be
blocked by default and permissions are given on a case by case basis.

Installation
============
 ``pip install django-failclose``

Setup
=====
#. Add ``failclose`` to INSTALLED_APPS
#. Add ``failclose.middlewares.FailCloseMiddlewares`` to your MIDDLEWARE_CLASSES
   setting
#. If you want to redirect to a certain page instead of returning a HTTP 403,
   set the FORBIDDEN_URL setting
#. To define a global permissions table, create a Python module with a RULES
   dictionary. Put the import path to that module in the PERMISSIONS_MODULE
   setting.

Usage
=====
Since by default all views are blocked, they need to be marked as safe.
There are two ways to do that:
#. Using the ``safe`` decorator on the view.
#. Including the view in the permissions module's RULES dictionary. In 
   the dict, keys are app names (or the project name in case of global 
   views) and values are lists of views. The views in the lists are
   whitelisted and, in the case of empty lists, all the views of that app
   are whitelisted.

A permissions file will look like this::

    RULES = {
        'app_name': ['view1', 'view2'],
        'app_name2': [], # all views are whitelisted
        'project_name': ['view1', 'view2'], # global views
    }

