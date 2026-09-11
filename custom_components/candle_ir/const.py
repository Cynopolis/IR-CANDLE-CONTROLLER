"""Constants for the LED Candle IR integration."""

from __future__ import annotations

DOMAIN = "candle_ir"

# Configuration keys
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"
CONF_DEVICE_TYPE = "device_type"


class CandleDeviceType:
    """Candle device types."""

    CANDLE = "candle"
    CANDLE_STRING = "candle_string"  # String of candles


# IR Command codes for LED candles
# These are placeholder values - replace with actual IR codes from your candle remotes
class CandleCommand:
    """IR command codes for LED candles."""

    # Power commands (common across most candle remotes)
    POWER = 0x45          # Power toggle (NEC protocol common value)
    POWER_ON = 0x46       # Explicit power on
    POWER_OFF = 0x47      # Explicit power off

    # Brightness commands
    BRIGHTNESS_UP = 0x11
    BRIGHTNESS_DOWN = 0x12

    # Color temperature (warm to cool)
    COLOR_TEMP_WARM = 0x1D
    COLOR_TEMP_COOL = 0x1E

    # Effect modes
    FLICKER = 0x0D        # Flame flicker effect
    FLAT = 0x0E           # Flat/steady light
    SNOWFLAKE = 0x0F      # Snowflake effect (if supported)

    # Numeric keypad for color selection on some remotes
    NUM_0 = 0x45
    NUM_1 = 0x09
    NUM_2 = 0x19
    NUM_3 = 0x0D
    NUM_4 = 0x1D
    NUM_5 = 0x05
    NUM_6 = 0x15
    NUM_7 = 0x07
    NUM_8 = 0x17
    NUM_9 = 0x44

    # Additional function keys
    TIMER_1H = 0x40
    TIMER_2H = 0x41
    TIMER_4H = 0x42
    TIMER_8H = 0x43
    MEM = 0x46            # Memory save
    PLAY = 0x47           # Cycle through modes

    @classmethod
    def to_nec_command(cls, code: int) -> dict[str, int]:
        """Convert a command code to NEC protocol format."""
        return {
            "address": 0xFAC0,  # Common LED candle remote address
            "command": code,
        }
