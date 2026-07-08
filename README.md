# No Post-Battle Spin — World of Tanks mod

Stops your tank from **turning in place after the battle ends**. If you're
holding a steering key when time runs out, a turretless tank (and, less
obviously, any tank) keeps pivoting on the spot while the results screen shows.
This mod freezes the hull the moment the battle ends.

## The bug

Turretless and limited-traverse tanks (TDs, SPGs) aim by **rotating the hull to
point the gun at the target**. When you aim past the gun's traverse, the client
continuously tells the server to *track the aim point with the gun*
(`VehicleGunRotator` → `cell.trackRelativePointWithGun` /
`vehicle_trackWorldPointWithGun`), and the server slews the hull to follow.
Stopping requires the client to send `stopTrackingOnServer()` →
`cell.vehicle_stopTrackingWithGun(...)`, which normally fires from the gun
rotator's tick loop when you stop aiming.

At battle end (`Avatar.py`): the arena period changes to `AFTERBATTLE`, which
calls `__setIsOnArena(False)` → `gunRotator.stop()`. That **cancels the gun
rotator's tick timer but never sends the stop-tracking command**. So the
server's last "track this point" order stays in effect and the hull keeps
turning while the results screen shows.

## The fix

The mod patches `PlayerAvatar.__onArenaPeriodChange`: after the original runs,
on `AFTERBATTLE` it calls `avatar.gunRotator.stopTrackingOnServer()` — the exact
stop command the cancelled tick loop would otherwise have sent — which tells the
server to hold the current yaw/pitch and stop slewing the hull. As a belt-and-
suspenders it also zeroes any latched manual steering-key input
(`vehicle.notifyInputKeysDown(0, 0, False)`). It only touches your own,
still-driving vehicle, and the patch is restored in `fini()`. Verified against
decompiled client scripts for **v2.3.0.1**.

## Install (for players)

Copy the built mod into your game's mods folder:

```
dist/de.tosox.no_post_battle_spin_1.0.0.wotmod
        ->  C:\Games\World_of_Tanks_EU\mods\2.3.0.1\
```

There's nothing to configure.

## Build (for developers)

Requires **Python 2.7** (compiles the game bytecode) and **Python 3** (runs the
script). Paths are configured at the top of `build.py`.

```bash
python build.py            # -> dist/de.tosox.no_post_battle_spin_1.0.0.wotmod
python build.py --install  # also copies the .wotmod into mods/<version>
```

`build.py` compiles `src/` into `build/py_stage/` and maps it into the game's
`res/` tree: the thin entry module goes to `scripts/client/gui/mods/`, and the
`no_post_battle_spin` package to `scripts/client/`. `meta.xml` is rendered from
`meta.xml.in`. All generated files land in `build/` (and `dist/`) — nothing
generated ever sits next to source.

## Testing

Watch `python.log` at the game root for the mod's output:

```
[no_post_battle_spin] battle-end hull stop armed
[no_post_battle_spin] loaded
```

To confirm end-to-end: take a **turretless** tank into a battle, drive so the
battle ends (or wait out the timer) while **holding a steering key**, and check
that the hull stops instead of pivoting as the results screen appears.

## Project layout

```
src/mod_no_post_battle_spin.py     thin entry point (init/fini) -> gui/mods/
src/no_post_battle_spin/           the mod package (Python 2.7) -> scripts/client/
  __init__.py                        NoPostBattleSpinMod lifecycle singleton (guarded)
  log.py                             tiny logging helper
  patch.py                           the AFTERBATTLE hull-stop patch
meta.xml.in                        .wotmod metadata template
build.py                           compile + package + install helper (Python 3)
build/                             generated artifacts (.pyc staging) - gitignored
dist/                              built .wotmod output - gitignored
```
