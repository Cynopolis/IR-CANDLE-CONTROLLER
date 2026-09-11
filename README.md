# LED Candle IR - Home Assistant Integration

[![HACS Default][hacs-badge]][hacs]
[![GitHub Workflow Status][action-badge]][action]

A HACS-customizable integration for controlling LED flame candles via infrared (IR) signals.

> **Adapted from:** [LG Infrared integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared) in Home Assistant Core.

## Features

- **Power Control** — Turn candles on/off via dedicated buttons
- **Effect Modes** — Toggle between flicker (flame) and flat (steady) modes
- **Brightness Control** — Select low/medium/high or use up/down buttons
- **Color Temperature** — Adjust warm/cool color temperature
- **Timer Functions** — Set auto-off timers (1h, 2h, 4h, 8h)
- **Multiple Devices** — Supports single candles and candle string sets

## Screenshots

<!-- Add screenshots once you have them -->

![Screenshot 1](docs/screenshot-1.png)

## Installation

### Via HACS (Recommended)

Have [HACS](https://hacs.xyz/) installed, this will allow you to update easily.

Adding LED Candle IR to HACS can be done using this button:

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=YOUR_USERNAME&repository=IR-Candle-Controller&category=integration)

> [!NOTE]
> If the button above doesn't work, add `https://github.com/YOUR_USERNAME/IR-Candle-Controller` as a custom repository of type **Integration** in HACS.

* Click **Download** on the **LED Candle IR** integration.
* Restart Home Assistant.
* Go to **Settings → Devices & Services → Add Integration** and search for "LED Candle IR"

### Manual Installation

1. Download the latest release ZIP from the [Releases page](https://github.com/YOUR_USERNAME/IR-Candle-Controller/releases)
2. Extract the `custom_components` folder
3. Copy it to your Home Assistant config directory:
   ```bash
   cp -r custom_components/candle_ir /config/custom_components/
   ```
4. Restart Home Assistant

## ⚠️ Important: Customizing IR Codes

The IR codes in `const.py` are **placeholder values**. You **must** replace them with the actual codes from your candle remote for this integration to work!

### How to find your remote's IR codes

1. **Use an IR receiver** (like a TSOP38238) connected to an ESPHome device or Raspberry Pi
2. **Use the Home Assistant `infrared` integration** to record raw signals from your remote
3. **Look up your remote's code** online (search for your remote model + "NEC codes")

### Common IR Remote Addresses for LED Candles

| Brand/Type | Address (hex) | Protocol |
|------------|---------------|----------|
| Generic Chinese remotes | `0xFAC0` | NEC |
| Some 4-key remotes | `0x00FF` | NEC |
| RGBW remotes | `0xE0E0` | NEC |

### To update the codes

Edit `custom_components/candle_ir/const.py`:

```python
class CandleCommand:
    # Update these with your remote's actual codes
    POWER = 0xXX          # Find this on your remote's power button
    POWER_ON = 0xXX
    POWER_OFF = 0xXX
    FLICKER = 0xXX
    FLAT = 0xXX
    # ... etc
```

## Configuration

After installation, add the integration via **Settings → Devices & Services**:

1. Click **Add Integration**
2. Search for **"LED Candle IR"**
3. Choose your device type:
   - **Single Candle** — for one candle with its own remote
   - **Candle String/Set** — for a string/set sharing one remote
4. Select an **IR emitter entity** (from your ESPHome IR blaster or similar)
5. Optionally select an **IR receiver entity** to detect physical remote commands

## Entities

### Buttons

| Entity | Description |
|--------|-------------|
| Power | Toggle power on/off |
| Power on | Explicit power on |
| Power off | Explicit power off |
| Flicker mode | Switch to flame flicker effect |
| Flat mode | Switch to steady light |
| Brightness up | Increase brightness |
| Brightness down | Decrease brightness |
| Color temp warm | Warmer color temperature |
| Color temp cool | Cooler color temperature |
| Timer 1-8h | Auto-off timers (disabled by default, enable in entity settings) |

### Select Entities

| Entity | Options |
|--------|---------|
| Effect mode | Flicker, Flat |
| Brightness | Low, Medium, High |

### Switch Entities

| Entity | Description |
|--------|-------------|
| Color temperature | Toggle between warm/cool (on=cool, off=warm) |

## Project Structure

```
IR-Candle-Controller/
├── .github/workflows/validate.yml   # HACS & Hassfest validation
├── .gitignore
├── CHANGELOG.md
├── hacs.json                        # HACS metadata
├── LICENSE
├── README.md
└── custom_components/
    └── candle_ir/                   # Integration domain
        ├── __init__.py              # Integration setup/teardown
        ├── button.py                # Button entities
        ├── config_flow.py           # UI configuration flow
        ├── const.py                 # Constants and IR command codes
        ├── entity.py                # Base entity class
        ├── manifest.json            # Home Assistant manifest
        ├── select.py                # Select entities (brightness, effects)
        └── strings.json             # Translations/UI strings
```

## Development

### Prerequisites

- Python 3.11+
- Home Assistant development environment
- An IR receiver to capture your remote's codes

### Running Validation Locally

```bash
# Install Home Assistant dev dependencies
pip install homeassistant[dev]

# Validate the manifest
python -m homeassistant.package_validation custom_components/
```

### Adding GitHub Actions

The included `.github/workflows/validate.yml` runs:
- **HACS validation** — checks HACS compliance
- **Hassfest validation** — checks Home Assistant integration standards

## Troubleshooting

### Integration not loading

1. Check the logs: **Settings → System → Logs**
2. Verify `custom_components/candle_ir/` exists in your config directory
3. Ensure all required files are present (see project structure above)
4. Restart Home Assistant

### IR commands not working

1. **Verify your IR codes** — The placeholder codes won't work with your remote
2. **Check emitter entity** — Make sure the selected IR emitter entity is available
3. **Test with Home Assistant's infrared integration** — Use the developer tools to send raw IR signals
4. **Enable debug logging**:

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.candle_ir: debug
```

### Duplicate entity errors

Make sure you haven't configured multiple candles pointing to the same IR emitter entity without distinct receiver entities.

## License

This project is licensed under the Apache 2.0 License. It is adapted from the Home Assistant Core LG Infrared integration.

## Acknowledgments

- [Home Assistant](https://www.home-assistant.io/) — The core platform
- [HACS](https://hacs.xyz/) — Community Store for Home Assistant
- [LG Infrared Integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared) — Source of the original integration this was adapted from

## Support

- [GitHub Issues](https://github.com/YOUR_USERNAME/IR-Candle-Controller/issues) — Bug reports and feature requests
- [Home Assistant Community Forum](https://community.home-assistant.io/) — General discussion

[hacs-badge]: https://img.shields.io/badge/HACS-Default-orange.svg?logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz
[action-badge]: https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/IR-Candle-Controller/ci.yml?branch=main&style=for-the-badge
[action]: https://github.com/YOUR_USERNAME/IR-Candle-Controller/actions
