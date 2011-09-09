# mapping between app names and the views considered safe
# if the app name is an empty string, the views are taken
# to be global, i.e. from a global views.py

RULES = {
    '': ['view1', 'views2'],
    'app_name': ['view1', 'view2'],
    'app_name2': [],
}
