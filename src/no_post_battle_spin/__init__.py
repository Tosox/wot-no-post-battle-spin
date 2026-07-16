from no_post_battle_spin.log import log
from no_post_battle_spin import patch
from no_post_battle_spin.util import safe


class NoPostBattleSpinMod(object):

    @safe
    def init(self):
        patch.apply_patch()
        log('loaded')

    @safe
    def fini(self):
        patch.remove_patch()
        log('unloaded')


g_noPostBattleSpinMod = NoPostBattleSpinMod()
