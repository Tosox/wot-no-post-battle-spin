# No Post-Battle Spin

[![Downloads (All Time)](https://img.shields.io/github/downloads/Tosox/wot-no-post-battle-spin/total.svg?label=Downloads%20(All%20Time))](https://github.com/Tosox/wot-no-post-battle-spin/releases) [![Downloads (Latest Release)](https://img.shields.io/github/downloads/Tosox/wot-no-post-battle-spin/latest/total.svg?label=Downloads%20(Latest%20Release))](https://github.com/Tosox/wot-no-post-battle-spin/releases/latest)

## 📜 Description

When a battle ends and the tank is still steering, it keeps pivoting
on the spot with the tracks still rolling, engine revving and dust flying.
It's most obvious on turretless tanks meaning TDs and SPGs which steer by rotating the hull.

This mod fixes this phenomenon by stopping every tank once the battle is over.

## 🔧 Installation

* Download the [latest release](https://github.com/Tosox/wot-no-post-battle-spin/releases/latest)
* Drop the `.wotmod` into your game's mods folder: `World_of_Tanks_EU\mods\<version>\`
* Launch the game

## 📝 Changelog

You can check out the latest changes in [`CHANGELOG.md`](CHANGELOG.md).

## 🎥 Preview

<img src="readme-res/preview.gif" alt="preview" width="700"/>

## 🛠️ Build from source

### Prerequisites

* [Python 2.7.18](https://www.python.org/downloads/release/python-2718/) — compiles the game bytecode

### Setup

1. Point the `PYTHON27` environment variable at your Python 2.7 executable
   (e.g. `C:\Python27\python.exe`). Skip this if you run `build.py` with Python 2.7 directly.
2. For `--install`, copy `build.local.example.json` to `build.local.json` and fill
   in your `game_dir` and `game_version`.

### Build

```bash
python build.py            # -> dist/<id>_<version>.wotmod
python build.py --install  # also copies it into the game's mods/<version> folder
```

The mod is configured through `mod.json`.

## ⚙️ How it works

The mod patches `PlayerAvatar.__onArenaPeriodChange`. When the arena period
changes to `AFTERBATTLE`, it walks every vehicle still alive in the arena and stops each one:

* `filter.reset()`: clears the client-side motion extrapolation
  that keeps remote tanks' hulls rotating after the server stops streaming updates
* `filter.ignoreInputs`: freezes your own hull, which is driven by the still-running
  local physics simulation
* `filter.setTracksSpeed(...)`: zeroes the track speed
* `trackScrollController.setData(None)`: clears the track-scroll texture, so the tracks stop
* `customEffectManager.disableDefaultSelectors(...)`: disables the dirt/dust particle selectors thrown up by the tracks
* `turnoffThrottle()`: cuts the engine-rev sound

## 📄 License

Distributed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for more information.
