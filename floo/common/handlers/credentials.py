import os
import sys
import webbrowser

try:
    from . import base
    from .. import api, shared as G, utils
    from ... import editor
    from ..protocols import floo_proto
    assert api and G and utils
except (ImportError, ValueError):
    import base
    from floo import editor
    from floo.common.protocols import floo_proto
    from .. import api, shared as G, utils

WELCOME_MSG = """Welcome %s!\n\nYou\'re all set to collaborate.

You may want to check out our docs at https://%s/help/plugins/#sublime-usage"""


class RequestCredentialsHandler(base.BaseHandler):
    PROTOCOL = floo_proto.FlooProtocol

    def __init__(self, token):
        super(RequestCredentialsHandler, self).__init__()
        self.token = token

    def build_protocol(self, *args):
        proto = super(RequestCredentialsHandler, self).build_protocol(*args)
        webbrowser.open('https://%s/dash/link_editor/%s/' % (proto.host, self.token))
        return proto

    def is_ready(self):
        return False

    def on_connect(self):
        self.send({
            'name': 'request_credentials',
            'client': self.client,
            'platform': sys.platform,
            'token': self.token,
            'version': G.__VERSION__
        })

    def on_data(self, name, data):
        if name == 'credentials':
            with open(G.FLOORC_PATH, 'wb') as floorc_fd:
                floorc = self.BASE_FLOORC + '\n'.join(['%s %s' % (k, v) for k, v in data['credentials'].items()]) + '\n'
                floorc_fd.write(floorc.encode('utf-8'))
            utils.reload_settings()
            if not G.USERNAME or not G.SECRET:
                editor.message_dialog('Something went wrong. See https://%s/help/floorc/ to complete the installation.' % self.proto.host)
                api.send_error({'message': 'No username or secret'})
            else:
                p = os.path.join(G.BASE_DIR, 'welcome.md')
                with open(p, 'wb') as fd:
                    text = WELCOME_MSG % (G.USERNAME, self.proto.host)
                    fd.write(text.encode('utf-8'))
                editor.active_window().open_file(p)
            self.proto.stop()
