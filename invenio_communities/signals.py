from __future__ import absolute_import, print_function

from blinker import Namespace

_signals = Namespace()

community_created = _signals.signal('community_created')
