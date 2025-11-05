# OSC Control for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

_Integration to control OSC-enabled hardware from Home Assistant._

**This integration will set up the following platforms:**

Platform | Description
-- | --
`button` | Trigger OSC messages with predefined values
`number` | Control OSC parameters with sliders/faders (0-1 range by default)

## Features

- 🎚️ **Sliders/Faders**: Control continuous parameters (volume, brightness, etc.)
- 🔘 **Buttons**: Trigger specific OSC commands
- 🌐 **Network-based**: Works over UDP/IP with any OSC-compatible device
- ⚙️ **Flexible**: Support for float, int, and bool value types
- 🏠 **Native HA Integration**: Full Home Assistant UI configuration support

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/ha_osc_control` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "OSC Control"
4. Enter your OSC server details:
   - **Device Name**: A friendly name for your OSC device
   - **Host**: IP address of your OSC-enabled hardware
   - **Port**: OSC port (default: 9000)

### Adding Entities

After setting up the integration, you can add buttons and sliders:

#### Via UI (Helper)

1. Go to **Settings** → **Devices & Services** → **Helpers**
2. Click **+ Create Helper**
3. Choose either:
   - **Button** for triggering OSC messages
   - **Number** for continuous control (sliders/faders)

#### Via YAML

You can also configure entities in your `configuration.yaml`:

```yaml
# Example Button
button:
  - platform: ha_osc_control
    name: "Trigger Effect"
    osc_address: "/fx/trigger"
    value: 1.0
    value_type: float

# Example Number (Slider)
number:
  - platform: ha_osc_control
    name: "Master Volume"
    osc_address: "/mix/volume"
    min: 0.0
    max: 1.0
    step: 0.01
    value_type: float
```

## Usage Examples

### Audio Mixing Console

Control volume faders and mute buttons on OSC-compatible mixing consoles:

```yaml
number:
  - platform: ha_osc_control
    name: "Channel 1 Volume"
    osc_address: "/ch/01/mix/fader"
    min: 0.0
    max: 1.0

button:
  - platform: ha_osc_control
    name: "Channel 1 Mute"
    osc_address: "/ch/01/mix/mute"
    value: 1
    value_type: int
```

### Lighting Control

Control OSC-enabled lighting systems:

```yaml
number:
  - platform: ha_osc_control
    name: "Stage Light Brightness"
    osc_address: "/light/1/intensity"
    min: 0
    max: 255
    value_type: int
```

### Video Projection

Control VJ software or video projectors:

```yaml
button:
  - platform: ha_osc_control
    name: "Next Scene"
    osc_address: "/scene/next"
    value: true
    value_type: bool
```

## Compatible Hardware/Software

This integration works with any device or software that supports OSC (Open Sound Control), including:

- **Audio**: QLab, Behringer X32, Midas M32, Allen & Heath dLive, etc.
- **Lighting**: GrandMA, ETC Eos, Chamsys MagicQ, etc.
- **Video**: Resolume, VDMX, TouchDesigner, etc.
- **Custom**: Any DIY project with OSC support (Arduino, Raspberry Pi, etc.)

## Support

- [Report a Bug][issues]
- [Suggest an Idea][issues]
- [Ask a Question][discussions]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/yourusername/ha-osc-control.svg?style=for-the-badge
[commits]: https://github.com/yourusername/ha-osc-control/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/yourusername/ha-osc-control.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/yourusername/ha-osc-control.svg?style=for-the-badge
[releases]: https://github.com/yourusername/ha-osc-control/releases
[issues]: https://github.com/yourusername/ha-osc-control/issues
[discussions]: https://github.com/yourusername/ha-osc-control/discussions
