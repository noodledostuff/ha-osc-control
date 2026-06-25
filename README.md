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

Use **v1.0.1 or newer** for current Home Assistant releases. It has been
verified with Home Assistant Core **2026.6.4** and fixes the button/slider
creation failure reported on Core **2025.12.3**. Earlier 0.2.x builds used a
removed Home Assistant platform setup API, so creating buttons/sliders from
Actions can fail on newer Home Assistant Core versions.

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

> **👉 For a complete step-by-step UI guide, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "OSC Control"
4. Enter your OSC server details:
   - **Device Name**: A friendly name for your OSC device
   - **Host**: IP address of your OSC-enabled hardware
   - **Port**: OSC port (default: 9000)

### Adding Controls

The integration uses a two-step process:

1. **Create OSC Endpoints** - Define target destinations and OSC addresses
2. **Create Controls** - Add buttons/sliders that trigger those endpoints

Endpoints, buttons, and sliders are created from **Developer Tools** →
**Actions**. The old **Developer Tools** → **Services** tab no longer exists in
current Home Assistant.

#### Step 1: Create OSC Endpoints

In **Developer Tools** → **Actions**, select `ha_osc_control.add_endpoint`.

```yaml
name: "Master Volume"
osc_address: "/mix/volume"
value_type: "float"
# host and port are optional (uses integration defaults)
```

Run the action again for each additional endpoint:

```yaml
name: "FX Trigger"
osc_address: "/fx/trigger"
value_type: "int"
```

Note the **endpoint_id** that appears in the logs. It is generated from the
config entry ID and OSC address, for example `/mix/volume` becomes
`your_entry_id__mix_volume`.

#### Step 2: Create Buttons and Sliders

```yaml
# Select ha_osc_control.add_slider
name: "Master Volume Fader"
endpoint_id: "your_entry_id__mix_volume"
min: 0.0
max: 1.0
step: 0.01
```

```yaml
# Select ha_osc_control.add_button
name: "Trigger Effect"
endpoint_id: "your_entry_id__fx_trigger"
value: 1
```

#### Via Automation

You can also create controls automatically when Home Assistant starts:

```yaml
automation:
  - alias: "Setup OSC Controls"
    trigger:
      - platform: homeassistant
        event: start
    action:
      # Create endpoints first
      - action: ha_osc_control.add_endpoint
        data:
          name: "Master Volume"
          osc_address: "/mix/volume"
      - action: ha_osc_control.add_endpoint
        data:
          name: "FX Trigger"
          osc_address: "/fx/trigger"
      # Then create controls
      - action: ha_osc_control.add_slider
        data:
          name: "Master Volume Fader"
          endpoint_id: "your_entry_id__mix_volume"
          min: 0.0
          max: 1.0
      - action: ha_osc_control.add_button
        data:
          name: "Trigger Effect"
          endpoint_id: "your_entry_id__fx_trigger"
          value: 1.0
```

## Usage Examples

### Audio Mixing Console

Control volume faders and mute buttons on OSC-compatible mixing consoles:

```yaml
# Create endpoints
action: ha_osc_control.add_endpoint
data:
  name: "Ch1 Volume"
  osc_address: "/ch/01/mix/fader"
  value_type: "float"
---
action: ha_osc_control.add_endpoint
data:
  name: "Ch1 Mute"
  osc_address: "/ch/01/mix/mute"
  value_type: "int"
---
# Create controls
action: ha_osc_control.add_slider
data:
  name: "Channel 1 Volume"
  endpoint_id: "your_entry_id__ch_01_mix_fader"
  min: 0.0
  max: 1.0
---
action: ha_osc_control.add_button
data:
  name: "Channel 1 Mute"
  endpoint_id: "your_entry_id__ch_01_mix_mute"
  value: 1
```

### Lighting Control

Control OSC-enabled lighting systems:

```yaml
action: ha_osc_control.add_endpoint
data:
  name: "Stage Light Brightness"
  osc_address: "/light/1/intensity"
  value_type: "int"
---
action: ha_osc_control.add_slider
data:
  name: "Stage Light Brightness"
  endpoint_id: "your_entry_id__light_1_intensity"
  min: 0
  max: 255
```

### Video Projection

Control VJ software or video projectors:

```yaml
action: ha_osc_control.add_endpoint
data:
  name: "Next Scene"
  osc_address: "/scene/next"
  value_type: "int"
---
action: ha_osc_control.add_button
data:
  name: "Next Scene"
  endpoint_id: "your_entry_id__scene_next"
  value: 1
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

[commits-shield]: https://img.shields.io/github/commit-activity/y/noodledostuff/ha-osc-control.svg?style=for-the-badge
[commits]: https://github.com/noodledostuff/ha-osc-control/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/noodledostuff/ha-osc-control.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/noodledostuff/ha-osc-control.svg?style=for-the-badge
[releases]: https://github.com/noodledostuff/ha-osc-control/releases
[issues]: https://github.com/noodledostuff/ha-osc-control/issues
[discussions]: https://github.com/noodledostuff/ha-osc-control/discussions

