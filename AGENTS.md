# AGENTS.md — LED Candle IR Integration

## Project Overview

This is a **HACS custom integration** for Home Assistant that controls LED flame candles via infrared (IR) signals. It was adapted from the [LG Infrared integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared) in Home Assistant Core.

The integration provides power control, effect mode selection, brightness adjustment, color temperature control, and timer functions through Home Assistant entities (buttons, selects, switches).

---

## ⚠️ CRITICAL: Folder Layout

**This project follows HACS conventions. The folder structure is non-negotiable.**

```
IR-Candle-Controller/                          ← Repository root
├── .github/workflows/validate.yml             ← CI: HACS + Hassfest validation
├── .gitignore
├── CHANGELOG.md                               ← Required by HACS submission
├── hacs.json                                  ← REQUIRED: HACS metadata (root level)
├── LICENSE
├── README.md
└── custom_components/                         ← REQUIRED by HACS
    └── candle_ir/                             ← Integration domain folder
        ├── __init__.py                        ← Entry point: async_setup_entry / async_unload_entry
        ├── button.py                          ← Button entities (power, effects, brightness)
        ├── config_flow.py                     ← UI setup wizard (menu-based device selection)
        ├── const.py                           ← Constants + IR command codes ⚠️ PLACEHOLDER VALUES
        ├── entity.py                          ← Base CandleEntity class (DeviceInfo, unique_id)
        ├── manifest.json                      ← HA manifest: domain, version, dependencies, codeowners
        ├── select.py                          ← Select entities (effect mode, brightness levels)
        ├── strings.json                       ← UI labels and translations
        └── switch.py                          ← Switch entities (color temperature toggle)
```

### Rules
- **Never move files outside `custom_components/candle_ir/`** — Home Assistant will not find them.
- **Never rename the `candle_ir` folder** — it must match the `"domain"` in `manifest.json`.
- **`hacs.json` MUST be at repository root** — HACS will not recognize the repo otherwise.
- All Python files use `from __future__ import annotations` (HA standard).

---

## Architecture Overview

### Integration Flow
1. User adds integration via config flow (`config_flow.py`)
2. User selects device type (single candle or candle string) and an IR emitter entity
3. `async_setup_entry()` in `__init__.py` forwards to platforms: `button`, `select`, `switch`
4. Each platform creates entities that inherit from `CandleEntity` (base class in `entity.py`)
5. Entities extend `InfraredEmitterConsumerEntity` from the HA `infrared` integration
6. When an entity action fires, it calls `self._send_command()` with a NEC protocol dict

### Entity Hierarchy
```
Entity (HA base)
 └── CandleEntity (entity.py) — adds DeviceInfo, unique_id construction
      └── InfraredEmitterConsumerEntity (HA infrared) — provides _send_command()
           ├── ButtonEntity  → CandleButton (button.py)
           ├── SelectEntity  → CandleEffectSelect, CandleBrightnessSelect (select.py)
           └── SwitchEntity  → CandleSwitch (switch.py)
```

### Key Dependencies
- **`infrared`** — Home Assistant core integration for IR emitter/receiver entities (declared in `manifest.json`)
- No external Python packages required

---

## ⚠️ CRITICAL: IR Command Codes

**The IR codes in `const.py` are PLACEHOLDER VALUES and will NOT work with real hardware.**

### Where to find them
All command codes live in the `CandleCommand` class in `/custom_components/candle_ir/const.py`:

```python
class CandleCommand:
    POWER = 0x45          # ← Placeholder — must be replaced
    POWER_ON = 0x46       # ← Placeholder
    FLICKER = 0x0D        # ← Placeholder
    # ... etc
```

### How codes are used
Each entity passes its command code through `CandleCommand.to_nec_command()`:

```python
# In button.py, select.py, switch.py — all follow this pattern:
await self._send_command(CandleCommand.to_nec_command(CandleCommand.POWER))
```

The `to_nec_command()` classmethod wraps the code into a NEC protocol dict:
```python
@classmethod
def to_nec_command(cls, code: int) -> dict[str, int]:
    return {"address": 0xFAC0, "command": code}
```

### How to get real codes
1. Use an IR receiver (TSOP38238) with ESPHome or a Raspberry Pi to capture raw signals
2. Use HA's `infrared` integration to record raw timings from the physical remote
3. Look up the remote model online for its NEC code table

### Common addresses for LED candle remotes
| Address (hex) | Notes |
|---------------|-------|
| `0xFAC0` | Most common generic Chinese remotes |
| `0x00FF` | Some 4-key remotes |
| `0xE0E0` | RGBW-style remotes |

**When modifying IR codes, update BOTH the code value AND the address if your remote uses a different one.**

---

## Platform Files Reference

### `__init__.py` — Entry Point
- Defines `PLATFORMS = [BUTTON, SELECT, SWITCH]`
- `async_setup_entry()` forwards to platforms
- `async_unload_entry()` unloads platforms
- No runtime data stored (IR is fire-and-forget, no state polling)

### `config_flow.py` — Setup Wizard
- Two-step flow: device type menu → IR entity selection
- Device types: `"candle"` (single) and `"candle_string"` (string/set)
- Uses HA's `EntitySelector` to let user pick from available IR emitters/receivers
- Config entry data stores: `device_type`, `infrared_entity_id`, `infrared_receiver_entity_id`

### `const.py` — Constants & IR Codes
- `DOMAIN = "candle_ir"` — must match manifest and folder name
- `CandleCommand` class — **all placeholder codes, must be customized**
- `to_nec_command()` — converts int code to NEC protocol dict

### `entity.py` — Base Class
- `CandleEntity(Entity)` — provides common `DeviceInfo` (manufacturer, model) and unique_id construction
- Unique ID format: `{entry.entry_id}_{unique_id_suffix}`

### `button.py` — Power & Function Buttons
- 5 always-enabled buttons: power toggle, power on, power off, flicker, flat
- 4 timer buttons (1h–8h): disabled by default, configurable in entity settings
- 2 brightness buttons: up/down
- 2 color temp buttons: warm/cool

### `select.py` — Dropdown Selectors
- `CandleEffectSelect`: options = ["flicker", "flat"]
- `CandleBrightnessSelect`: options = ["low", "medium", "high"]
- Both implement `RestoreEntity` for state persistence across restarts

### `switch.py` — Toggle Switches
- `CandleSwitch` for color temperature (on=cool, off=warm)
- Designed to be extended with additional on/off switches if the remote supports them

### `strings.json` — UI Labels
- All button, select, and switch display names
- Config flow titles and descriptions
- Uses HA key references (`[%key:common::...%]`) where appropriate

---

## HACS Requirements

### Required Files (must exist)
| File | Location | Purpose |
|------|----------|---------|
| `hacs.json` | Repository root | HACS metadata and version constraints |
| `custom_components/candle_ir/manifest.json` | Integration dir | HA integration manifest |
| `README.md` | Repository root | Installation and usage documentation |

### hacs.json fields
```json
{
  "name": "LED Candle IR",
  "zip_release": true,
  "hide_default_branch": false,
  "homeassistant": "2024.6.0",     ← Minimum HA version
  "hacs": "1.34.0",                ← Minimum HACS version
  "filename": "candle_ir.zip"
}
```

### manifest.json required fields
- `domain` — must match folder name
- `name`, `version`, `config_flow`, `documentation`, `codeowners`, `iot_class`, `integration_type`
- `dependencies: ["infrared"]` — declares the HA infrared integration dependency

### Publishing to HACS
1. Create a GitHub release: `git tag v1.0.0 && git push origin v1.0.0`
2. Submit to HACS default repo: https://github.com/hacs/default/issues/new?template=integration.md
3. Register brand with home-assistant/brands (required for HACS approval)

---

## CI / Validation

Three GitHub Actions workflows live in `.github/workflows/`:

### `ci.yml` — Full CI Pipeline (adapted from HASS-Habit-Tracker)
Runs on push/PR to `main` or `develop`. Five jobs:
1. **json** — validates every `.json` file parses correctly
2. **py_compile** — runs `python -m py_compile` on all `.py` files in `custom_components/` across Python 3.12 and 3.13
3. **lint** — runs `ruff check` (fails on errors) and `ruff format --check` (warns only)
4. **schema** — validates `manifest.json` (domain matches folder, version present) and `hacs.json` (name present)
5. **structure** — checks all required integration files exist (`__init__.py`, `manifest.json`, `button.py`, `select.py`, `switch.py`, `config_flow.py`, `strings.json`, `hacs.json`, `README.md`, `LICENSE`)

A final **status** job reports combined pass/fail.

### `release.yml` — Automated GitHub Releases (adapted from HASS-Habit-Tracker)
Runs on push to `main` or manually via `workflow_dispatch`. Creates a GitHub Release:
1. Reads version from `custom_components/candle_ir/manifest.json`
2. Checks if release `v{version}` already exists (skips if so)
3. Zips `custom_components/candle_ir/` → `candle_ir.zip`
4. Uploads the zip as a release asset via `softprops/action-gh-release@v2`

### `validate.yml` — HACS + Hassfest Basic Validation
Runs on every push/PR. Two jobs:
- **hacs** — validates HACS compliance via `hacs/action`
- **hassfest** — validates HA integration standards via `home-assistant/actions/hassfest`

---

## Common Modification Patterns

### Adding a new button
1. Add a new constant to `CandleCommand` in `const.py`
2. Add a `CandleButtonEntityDescription` entry to the appropriate tuple in `button.py`
3. It will automatically appear in `ALL_BUTTON_DESCRIPTIONS` (timer/brightness/color groups are concatenated)

### Adding a new select option
1. Add the mapping to `EFFECT_MODES` or `BRIGHTNESS_COMMANDS` dict in `select.py`
2. The `_attr_options` property auto-generates from the dict keys

### Adding a new switch
1. Add an entry to `CANDLE_SWITCH_DESCRIPTIONS` in `switch.py`
2. Define `on_code` and optionally `off_code` using `CandleCommand` constants

### Changing IR address
Edit the `address` field in `CandleCommand.to_nec_command()` in `const.py`.

### Adding a new device type
1. Add to `DEVICE_TYPE_NAMES` in `config_flow.py`
2. Add a new `async_step_<type>()` method following the candle/candle_string pattern
3. Update `menu_options` in `async_step_user()`

---

## Testing

### Manual testing steps
1. Copy `custom_components/candle_ir/` to your HA config's `custom_components/` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → "LED Candle IR"
4. Verify entities appear in the device registry
5. Press buttons/select options and verify IR signals are emitted (check ESPHome logs or use an IR receiver)

### Debug logging
Add to `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.candle_ir: debug
```

---

## License & Attribution

Licensed under Apache 2.0. Adapted from the Home Assistant Core [LG Infrared integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared).
