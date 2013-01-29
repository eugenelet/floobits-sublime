import os
import json

import sublime

from . import shared as G

per_path = os.path.abspath('persistent.json')


def get_full_path(p):
    full_path = os.path.join(G.PROJECT_PATH, p)
    return unfuck_path(full_path)


def unfuck_path(p):
    return os.path.normcase(os.path.normpath(p))


def to_rel_path(p):
    return p[len(G.PROJECT_PATH) + 1:]


def to_scheme(secure):
    if secure is True:
        return 'https'
    return 'http'


def is_shared(p):
    if not G.CONNECTED:
        return False
    p = unfuck_path(p)
    return G.PROJECT_PATH == p[:len(G.PROJECT_PATH)]


def get_persistent_data():
    try:
        per = open(per_path, 'rb')
    except (IOError, OSError):
        return {}
    try:
        persistent_data = json.loads(per.read())
    except:
        return {}
    return persistent_data


def update_persistent_data(data):
    with open(per_path, 'wb') as per:
        per.write(bytes(json.dumps(data), 'UTF-8'))


def rm(path):
    """removes path and dirs going up until a OSError"""
    os.remove(path)
    try:
        os.removedirs(os.path.split(path)[0])
    except OSError as e:
        if e.errno != 66:
            sublime.error_message('Can not delete directory {0}.\n{1}'.format(path, e))
            raise


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            sublime.error_message('Can not create directory {0}.\n{1}'.format(path, e))
            raise
