# OSC Control - UI Setup Guide

This guide walks you through setting up OSC Control entirely through the Home Assistant UI.

## Step 1: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "OSC Control"
4. Enter your OSC device information:
   - **Device Name**: e.g., "My Mixing Console"
   - **Host**: IP address of your OSC device (e.g., `192.168.1.100`)
   - **Port**: OSC port (default: `9000`)
5. Click **Submit**

## Step 2: Create OSC Endpoints

OSC endpoints define the destinations (OSC addresses) that your buttons and sliders will control.

1. Go to **Developer Tools** → **Services**
2. Select service: `ha_osc_control.add_endpoint`
3. Fill in the form:
   - **Name**: Descriptive name (e.g., "Master Volume")
   - **OSC Address**: The OSC path (e.g., `/mix/volume`)
   - **Value Type**: Choose `float`, `int`, or `bool`
   - **Host/Port**: Leave empty to use integration defaults, or specify different target
4. Click **Call Service**
5. Repeat for each OSC endpoint you want to control

### Finding Endpoint IDs

After creating endpoints, you need their IDs to create controls:

1. Go to **Developer Tools** → **Services**
2. Select service: `ha_osc_control.list_endpoints`
3. Click **Call Service**
4. Check **Settings** → **System** → **Logs** to see all endpoint IDs

The endpoint ID format is: `{entry_id}_{osc_address_with_underscores}`

Example: `abc123_/mix/volume` becomes `abc123__mix_volume`

## Step 3: Create Buttons

Buttons trigger OSC messages with a specific value when pressed.

1. Go to **Developer Tools** → **Services**
2. Select service: `ha_osc_control.add_button`
3. Fill in the form:
   - **Name**: Button name (e.g., "Trigger Effect")
   - **Endpoint ID**: Copy from the logs (Step 2)
   - **Value**: The value to send (e.g., `1.0`)
4. Click **Call Service**

The button will appear as an entity in Home Assistant!

## Step 4: Create Sliders

Sliders provide continuous control over OSC parameters.

1. Go to **Developer Tools** → **Services**
2. Select service: `ha_osc_control.add_slider`
3. Fill in the form:
   - **Name**: Slider name (e.g., "Master Volume")
   - **Endpoint ID**: Copy from the logs (Step 2)
   - **Min**: Minimum value (e.g., `0.0`)
   - **Max**: Maximum value (e.g., `1.0`)
   - **Step**: Increment (e.g., `0.01`)
4. Click **Call Service**

The slider will appear as a number entity in Home Assistant!

## Step 5: Add to Dashboard

1. Go to your dashboard
2. Click **Edit Dashboard** (top right)
3. Click **+ Add Card**
4. Choose **Entities Card**
5. Add your buttons and sliders
6. Click **Save**

## Example: Audio Mixing Console

### Create Endpoints
```
Service: ha_osc_control.add_endpoint
- Name: "Channel 1 Volume"
- OSC Address: "/ch/01/mix/fader"
- Value Type: float

Service: ha_osc_control.add_endpoint
- Name: "Channel 1 Mute"
- OSC Address: "/ch/01/mix/mute"
- Value Type: int
```

### List Endpoints (check logs)
```
Service: ha_osc_control.list_endpoints
```

### Create Controls
```
Service: ha_osc_control.add_slider
- Name: "Ch1 Volume"
- Endpoint ID: (from logs)
- Min: 0.0
- Max: 1.0
- Step: 0.01

Service: ha_osc_control.add_button
- Name: "Ch1 Mute"
- Endpoint ID: (from logs)
- Value: 1
```

## Automation Setup

You can also create controls automatically when Home Assistant starts:

1. Go to **Settings** → **Automations & Scenes**
2. Click **+ Create Automation**
3. Choose **Start from scratch**
4. Add trigger: **Home Assistant Start**
5. Add actions using the service calls above
6. Save the automation

This way, your controls will be recreated every time Home Assistant restarts!

## Tips

- **Test OSC messages**: Use a tool like [OSC Monitor](http://www.kasperkamperman.com/blog/processing-code/osc-datamonitor/) to verify your OSC device is receiving messages
- **Check logs**: If something isn't working, check **Settings** → **System** → **Logs** for error messages
- **Organize endpoints**: Use descriptive names for endpoints to make them easier to manage
- **Multiple devices**: You can add multiple OSC Control integrations for different devices

## Troubleshooting

**Q: I don't see my button/slider entities**
- Check logs for errors
- Verify endpoint ID is correct
- Restart Home Assistant if needed

**Q: OSC messages aren't being received**
- Verify host and port are correct
- Check network connectivity
- Ensure OSC device is listening

**Q: How do I remove a button/slider?**
- Go to **Settings** → **Devices & Services** → **Entities**
- Find the entity and delete it

**Q: How do I change endpoint settings?**
- Currently you need to create a new endpoint with different settings
- Future updates will add endpoint management
