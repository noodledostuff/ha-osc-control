# OSC Control

Control OSC-enabled hardware directly from Home Assistant.

Current release: **v1.0.1**.

## Features

- 🎚️ **Sliders/Faders** for continuous control
- 🔘 **Buttons** for triggering commands
- 🌐 Works with any OSC-compatible device
- ⚙️ Support for float, int, and bool values
- 🧰 Endpoints and controls are created from Home Assistant **Actions**

## Compatible With

- Audio consoles (Behringer X32, Midas, etc.)
- Lighting systems (GrandMA, ETC, etc.)
- VJ software (Resolume, VDMX, etc.)
- DIY OSC projects

## Quick Setup

1. Add the integration via UI
2. Enter your OSC device IP and port
3. Use **Developer Tools** → **Actions** to create OSC endpoints
4. Use those endpoint IDs to create buttons and sliders
5. Control your hardware from Home Assistant!

Use v1.0.1 or newer on current Home Assistant releases. Older 0.2.x builds can
fail when creating buttons or sliders from Actions.

Perfect for home theaters, studios, stage setups, and custom automation projects.
