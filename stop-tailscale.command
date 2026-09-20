#!/bin/zsh
set -e

if command -v tailscale >/dev/null 2>&1; then
    tailscale_cmd="$(command -v tailscale)"
elif [[ -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ]]; then
    tailscale_cmd=/Applications/Tailscale.app/Contents/MacOS/Tailscale
else
    echo "Tailscale is not installed."
    read -k 1 "?Press any key to close."
    exit 1
fi

echo "Stopping private Tailscale access to Wordwell..."
if ! "$tailscale_cmd" serve reset; then
    echo
    echo "Tailscale could not remove the Wordwell Serve route."
    read -k 1 "?Press any key to close."
    exit 1
fi
echo
"$tailscale_cmd" serve status
echo
echo "Wordwell is no longer shared through Tailscale. Tailscale itself remains connected."
read -k 1 "?Press any key to close."
echo
