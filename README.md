# LED Candle IR Controller for Home Assistant

An Home Assistant custom integration for controlling LED flame candles via infrared (IR) signals.

## Overview

This integration is adapted from the [LG Infrared integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared) from Home Assistant Core. It provides a clean way to control your IR-enabled LED candles through Home Assistant.

## Features

- **Power Control**: Turn candles on/off
- **Brightness Control**: Adjust brightness levels (low/medium/high) or use up/down buttons
- **Effect Modes**: Toggle between flicker (flame) and flat (steady) modes
- **Color Temperature**: Adjust warm/cool color temperature
- **Timer Functions**: Set auto-off timers (1h, 2h, 4h, 8h) - optional entities

## Installation

1. Copy the `candle_ir` folder to your Home Assistant `custom_components` directory:
   ```bash
   cp -r candle_ir /path/to/home-assistant/config/custom_components/
   ```

2. Restart Home Assistant

3. Go to **Settings → Devices & Services → Add Integration**

4. Search for "LED Candle IR" and follow the setup wizard

## ⚠️ Important: Customizing IR Codes

The IR codes in `const.py` are **placeholder values**. You MUST replace them with the actual codes from your candle remote!

### How to find your remote's IR codes:

1. **Use an IR receiver** (like a TSOP38238) connected to an ESPHome device or Raspberry Pi
2. **Use the Home Assistant `infrared` integration** to record raw signals
3. **Look up your remote's code** online (search for your remote model + "NEC codes")

### Common IR Remote Addresses for LED Candles:

| Brand/Type | Address (hex) | Protocol |
|------------|---------------|----------|
| Generic Chinese remotes | `0xFAC0` | NEC |
| Some 4-key remotes | `0x00FF` | NEC |
| RGBW remotes | `0xE0E0` | NEC |

### To update the codes:

Edit `/custom_components/candle_ir/const.py`:

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

## Entity Summary

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
| Timer 1-8h | Auto-off timers (disabled by default) |

### Select Entities
| Entity | Options |
|--------|---------|
| Effect mode | Flicker, Flat |
| Brightness | Low, Medium, High |

### Switch Entities
| Entity | Description |
|--------|-------------|
| Color temperature | Toggle between warm/cool (on=cool, off=warm) |

## File Structure

```
candle_ir/
├── __init__.py          # Integration setup/teardown
├── button.py            # Button entities (power, effects, etc.)
├── config_flow.py       # UI configuration flow
├── const.py             # Constants and IR command codes
├── entity.py            # Base entity class
├── manifest.json        # Integration metadata
├── select.py            # Select entities (brightness, effects)
├── strings.json         # Translations/UI strings
└── switch.py            # Switch entities
```

## Development Notes

This integration was adapted from the LG Infrared component. Key differences:
- Simplified platform set (no climate/media_player needed for candles)
- Custom IR command codes for candle remotes
- Effect mode and brightness select entities
- Timer function buttons

## License

This project is adapted from Home Assistant Core, which is licensed under the Apache 2.0 license.
