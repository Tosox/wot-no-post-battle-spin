from no_post_battle_spin.log import log

# Fix: in a turretless / limited-traverse tank, if the hull is auto-rotating to
# follow the gun when the battle ends while you are alive, on the results screen
# the hull keeps pivoting AND the road wheels, track band, and engine keep
# running. Root cause: at battle end the game stops accepting input, but the own
# vehicle's client filter holds a latched non-zero motion state
# (angularSpeed / movementInfo) that nothing cancels, so every motion-driven
# visual keeps animating off it.
#
# We stop each subsystem at AFTERBATTLE. Several of these methods are never
# called by the game's own code and were found by dir() introspection of the
# live C++ objects:
#   filter.ignoreInputs = True               -> freezes the hull rotation
#   filter.velocityErrorCompensation = 100   -> snap to server (what death does)
#   filter.setTracksSpeed(0, True, 0, True)  -> stops the track band scroll
#   trackScrollController.setData(None)       -> stops the track TEXTURE scroll
#   wheelsAnimator.stopAnimatingWheels(True, True)
#                                             -> stops road wheels + the
#                                                track-link nodes that follow them
#   detailedEngineState.throttle = 0
#   physics.movementSignals = 0               -> engine "is-moving" bitmask off
#
# HARD-WON WARNINGS (do NOT reintroduce -- each crashes the client at battle end
# or is a proven no-op):
#   * reading  physics.angVelocity / any physics velocity getter -> CRASH
#   * writing  physics.isFrozen = True                           -> CRASH
#   * writing  physics.isAutorotation = False                    -> CRASH
#   * physics.staticMode / filter.enableClientFilters=False / filter.reset()
#     / filter.setVehiclePhysics(None)                           -> no-op or worse
#   physics.movementSignals = 0 is the ONE physics write proven safe.

_METHOD = '_PlayerAvatar__onArenaPeriodChange'
_orig = None


def _try(fn, what):
    try:
        fn()
    except Exception:
        import traceback
        log('post-battle stop: %s failed:\n%s' % (what, traceback.format_exc()))


def _stop_own_vehicle(avatar):
    import BigWorld
    try:
        vehicle = BigWorld.entity(avatar.playerVehicleID)
    except Exception:
        vehicle = None
    if vehicle is None:
        return
    filt = getattr(vehicle, 'filter', None)
    app = getattr(vehicle, 'appearance', None)

    if filt is not None:
        if hasattr(filt, 'velocityErrorCompensation'):
            _try(lambda: setattr(filt, 'velocityErrorCompensation', 100.0), 'velocityErrorCompensation')
        if hasattr(filt, 'ignoreInputs'):
            _try(lambda: setattr(filt, 'ignoreInputs', True), 'ignoreInputs')
        if hasattr(filt, 'setTracksSpeed'):
            _try(lambda: filt.setTracksSpeed(0.0, True, 0.0, True), 'setTracksSpeed')

    if app is not None:
        tsc = getattr(app, 'trackScrollController', None)
        if tsc is not None:
            _try(lambda: tsc.setData(None), 'trackScroll.setData(None)')
        wa = getattr(app, 'wheelsAnimator', None)
        if wa is not None and hasattr(wa, 'stopAnimatingWheels'):
            _try(lambda: wa.stopAnimatingWheels(True, True), 'stopAnimatingWheels')
        des = getattr(app, 'detailedEngineState', None)
        if des is not None:
            _try(lambda: setattr(des, 'throttle', 0), 'throttle')
        # stop the track dust/dirt + exhaust effects. disableCustomEffects only
        # stop()s SETTING_DUST selectors, but CustomEffectManager.update() runs
        # every frame off the latched track slip/contact and re-drives them.
        # disableDefaultSelectors(True, True) DESTROYS the chassis+hull effect
        # selectors and removes them from the update list, so nothing re-emits.
        if hasattr(app, 'disableCustomEffects'):
            _try(lambda: app.disableCustomEffects(), 'disableCustomEffects')
        cem = getattr(app, 'customEffectManager', None)
        if cem is not None and hasattr(cem, 'disableDefaultSelectors'):
            _try(lambda: cem.disableDefaultSelectors(True, True), 'disableDefaultSelectors')

    # engine "is-moving" bitmask -- the one physics write proven safe.
    if filt is not None:
        def _movesig():
            phys = filt.getVehiclePhysics()
            if phys is not None:
                phys.movementSignals = 0
        _try(_movesig, 'movementSignals')
    log('post-battle stop applied')


def _patched_onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
    try:
        from constants import ARENA_PERIOD
        is_after = period == ARENA_PERIOD.AFTERBATTLE
    except Exception:
        is_after = False
    _orig(self, period, periodEndTime, periodLength, periodAdditionalInfo)
    if is_after:
        try:
            _stop_own_vehicle(self)
        except Exception:
            import traceback
            log('post-battle stop crashed:\n' + traceback.format_exc())


def apply_patch():
    global _orig
    try:
        from Avatar import PlayerAvatar
    except Exception as e:
        log('could not import PlayerAvatar, mod inactive: ' + str(e))
        return False
    if _orig is None:
        _orig = getattr(PlayerAvatar, _METHOD)
    setattr(PlayerAvatar, _METHOD, _patched_onArenaPeriodChange)
    log('battle-end vehicle stop armed')
    return True


def remove_patch():
    global _orig
    if _orig is None:
        return
    try:
        from Avatar import PlayerAvatar
        setattr(PlayerAvatar, _METHOD, _orig)
        log('battle-end vehicle stop removed')
    except Exception as e:
        log('failed to restore: ' + str(e))
    _orig = None
