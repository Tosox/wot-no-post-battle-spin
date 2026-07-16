from no_post_battle_spin.log import log
from no_post_battle_spin.util import safe


_METHOD = '_PlayerAvatar__onArenaPeriodChange'
_oPlayerAvatar__onArenaPeriodChange = None


_POLL = 0.05
_ROT_MIN = 0.1
_TIMEOUT = 3.0
_FREEZE_DELAY = 0.25


def _is_pivoting(vehicle):
    veh_filter = vehicle.filter
    left = veh_filter.leftTrackScroll
    right = veh_filter.rightTrackScroll

    # Check if the vehicle is pivoting by comparing the scroll directions of the
    # left and right tracks and if the rotation speed exceeds the minimum threshold
    return left * right < 0.0 and abs(veh_filter.instantaneousRotationSpeed) > _ROT_MIN


def _stop_vehicle(vehicle):
    veh_filter = vehicle.filter
    veh_appearance = vehicle.appearance

    # Stop hull rotation
    veh_filter.reset()
    veh_filter.ignoreInputs = True

    # Stop tracks from moving
    veh_filter.setTracksSpeed(0.0, False, 0.0, False)
    veh_appearance.trackScrollController.setData(None)

    # Disable dirt particles thrown by tracks
    veh_appearance.customEffectManager.disableDefaultSelectors(True, True)


def _live_vehicle(vehicle_id):
    import BigWorld
    veh = BigWorld.entities.get(vehicle_id)
    return veh if (veh and veh.isStarted and veh.isAlive()) else None


@safe
def _stop_when_settled(vehicle_id):
    import BigWorld

    # Skip destroyed or non-existent vehicles
    vehicle = _live_vehicle(vehicle_id)
    if not vehicle:
        return

    # Skip vehicles with a full 360-degree turret
    if vehicle.typeDescriptor.gun.turretYawLimits is None:
        return

    deadline = BigWorld.time() + _TIMEOUT

    @safe
    def _apply_stop():
        # Re-check if the vehicle is still alive before stopping it
        veh = _live_vehicle(vehicle_id)
        if veh:
            _stop_vehicle(veh)

    @safe
    def _poll():
        # Re-check if the vehicle is still alive before polling
        veh = _live_vehicle(vehicle_id)
        if not veh:
            return

        # Check if the vehicle is pivoting or if the timeout has been reached
        if _is_pivoting(veh) or BigWorld.time() >= deadline:
            # Stop the vehicle after a short delay to ensure it has settled
            BigWorld.callback(_FREEZE_DELAY, _apply_stop)
        else:
            # Continue polling
            BigWorld.callback(_POLL, _poll)

    # Start polling for the vehicle to settle
    BigWorld.callback(_POLL, _poll)


@safe
def _handle_period_change(avatar, period):
    from constants import ARENA_PERIOD

    # Try settle valid vehicles when the battle ends
    if period == ARENA_PERIOD.AFTERBATTLE:
        for vehicle_id in avatar.arena.vehicles:
            _stop_when_settled(vehicle_id)


def _patched_onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
    _oPlayerAvatar__onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo)
    _handle_period_change(self, period)


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
