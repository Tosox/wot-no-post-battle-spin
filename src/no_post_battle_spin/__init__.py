from no_post_battle_spin.log import log


class NoPostBattleSpinMod(object):

    def init(self):
        try:
            from no_post_battle_spin import patch
            patch.apply_patch()
            log('loaded')
        except Exception:
            import traceback
            log('init failed:\n' + traceback.format_exc())

    def fini(self):
        try:
            from no_post_battle_spin import patch
            patch.remove_patch()
            log('unloaded')
        except Exception:
            import traceback
            log('fini failed:\n' + traceback.format_exc())


g_noPostBattleSpinMod = NoPostBattleSpinMod()
