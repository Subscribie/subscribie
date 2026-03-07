#!/usr/bin/env bash
# stop_stripe_listener.sh
# Script to easily stop the stripe listener running in the background.

PID_FILE=".stripe_listen.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "Stopping Stripe listener (PID: $PID)..."
        kill $PID
        rm "$PID_FILE"
        echo "✅ Stopped."
    fi
else
    echo "Stripe listener not currently running (no $PID_FILE found)."
fi