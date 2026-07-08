from no_post_battle_spin.log import log


_METHOD = '_PlayerAvatar__onArenaPeriodChange'
_oPlayerAvatar__onArenaPeriodChange = None


def _stop_vehicle(vehicle):
    veh_filter = vehicle.filter
    veh_appearance = vehicle.appearance

    # Stop hull rotation
    veh_filter.ignoreInputs = True

    # Stop tracks from moving
    veh_filter.setTracksSpeed(0.0, True, 0.0, True)
    veh_appearance.trackScrollController.setData(None)

    # Disable dirt particles thrown by tracks
    veh_appearance.customEffectManager.disableDefaultSelectors(True, True)

    # Stop engine sound
    vehicle.turnoffThrottle()


def _stop_all_vehicles(avatar):
    import BigWorld

    for vehicle_id in avatar.arena.vehicles:
        vehicle = BigWorld.entities.get(vehicle_id)
        if vehicle and vehicle.isStarted and vehicle.isAlive():
            _stop_vehicle(vehicle)

    log('post-battle stop applied')


def _patched_onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
    _oPlayerAvatar__onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo)
    try:
        from constants import ARENA_PERIOD
        if period == ARENA_PERIOD.AFTERBATTLE:
            _stop_all_vehicles(self)
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
