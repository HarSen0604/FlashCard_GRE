#!/bin/zsh
set -e

if command -v tailscale >/dev/null 2>&1; then
    tailscale_cmd="$(command -v tailscale)"
elif [[ -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ]]; then
    tailscale_cmd=/Applications/Tailscale.app/Contents/MacOS/Tailscale
else
    echo "Tailscale is not installed. Install and connect it before running this file."
    read -k 1 "?Press any key to close."
    exit 1
fi

if ! "$tailscale_cmd" status >/dev/null; then
    echo "Tailscale is not connected. Open Tailscale and connect this Mac first."
    read -k 1 "?Press any key to close."
    exit 1
fi

echo "Starting private Tailscale access to Wordwell on port 5055..."
if ! "$tailscale_cmd" serve --bg 5055; then
    echo
    echo "Tailscale could not start Serve. Follow any enablement link shown above, then run this file again."
    read -k 1 "?Press any key to close."
    exit 1
fi
echo
"$tailscale_cmd" serve status
echo
echo "Wordwell is available only to authenticated devices in your tailnet."
echo "Keep run.command running in its other Terminal window."
read -k 1 "?Press any key to close."
echo
