from no_post_battle_spin.log import log


_METHOD = '_PlayerAvatar__onArenaPeriodChange'
_oPlayerAvatar__onArenaPeriodChange = None


def _stop_own_vehicle(avatar):
    import BigWorld
    vehicle = BigWorld.entity(avatar.playerVehicleID)
    if vehicle is None:
        return

    veh_filter = vehicle.filter
    veh_appearance = vehicle.appearance

    # Stop the vehicle from spinning
    veh_filter.ignoreInputs = True                    # freeze hull rotation (primary fix)
    veh_filter.velocityErrorCompensation = 100.0      # snap to server (what death does)

    # Stop the tracks from moving
    veh_filter.setTracksSpeed(0.0, True, 0.0, True)   # stop track band scroll
    veh_appearance.trackScrollController.setData(None)          # stop track texture scroll
    veh_appearance.wheelsAnimator.stopAnimatingWheels(True, True)   # road wheels + track nodes

    # Disable dirt particles thrown by tracks
    veh_appearance.disableCustomEffects()
    veh_appearance.customEffectManager.disableDefaultSelectors(True, True)

    # Stop the engine sound
    vehicle.turnoffThrottle()
    veh_physics = veh_filter.getVehiclePhysics()
    if veh_physics is not None:
        veh_physics.movementSignals = 0                # engine "is-moving" bitmask off

    log('post-battle stop applied')


def _patched_onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
    _oPlayerAvatar__onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo)
    try:
        from constants import ARENA_PERIOD
        if period == ARENA_PERIOD.AFTERBATTLE:
            _stop_own_vehicle(self)
    except Exception:
        import traceback
        log('post-battle stop crashed:\n' + traceback.format_exc())


def apply_patch():
    global _oPlayerAvatar__onArenaPeriodChange
    
    from Avatar import PlayerAvatar
    if _oPlayerAvatar__onArenaPeriodChange is None:
        _oPlayerAvatar__onArenaPeriodChange = getattr(PlayerAvatar, _METHOD)

    setattr(PlayerAvatar, _METHOD, _patched_onArenaPeriodChange)


def remove_patch():
    global _oPlayerAvatar__onArenaPeriodChange
    if _oPlayerAvatar__onArenaPeriodChange is None:
        return

    from Avatar import PlayerAvatar
    setattr(PlayerAvatar, _METHOD, _oPlayerAvatar__onArenaPeriodChange)

    _oPlayerAvatar__onArenaPeriodChange = None
