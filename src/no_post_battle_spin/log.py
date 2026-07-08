import sys

TAG = '[no_post_battle_spin]'


def log(msg):
    print(TAG + ' ' + msg)
    # Flush so lines survive a native (C++) crash -- otherwise the last buffered
    # lines (which name the call that crashed) are lost.
    try:
        sys.stdout.flush()
    except Exception:
        pass
