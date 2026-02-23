#!/usr/bin/env bash
# start_stripe_listener.sh
# Script to easily run stripe listen in the background for local development.

LOG_FILE="stripe_listen.log"
PID_FILE=".stripe_listen.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null; then
        echo "Stripe listener is already running with PID $OLD_PID."
        echo "Stop it first with: ./stop_stripe_listener.sh"
        exit 1
    else
        # Process died but pid file remains, clean up
        rm "$PID_FILE"
    fi
fi

echo "Starting Stripe CLI listener..."

# If STRIPE_TEST_SECRET_KEY is not in environment, fail and exit
if [ -z "$STRIPE_TEST_SECRET_KEY" ]; then
    echo "STRIPE_TEST_SECRET_KEY is not set. Please set it in your environment."
    exit 1
fi

# Run stripe listen in the background
# We use nohup so that closing the terminal doesn't kill it
nohup stripe listen \
  --api-key "${STRIPE_TEST_SECRET_KEY}" \
  --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed,invoice.created \
  --forward-to 127.0.0.1:5000/stripe_webhook \
  --forward-connect-to 127.0.0.1:5000/stripe_webhook > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo "✅ Stripe listener started in background (PID: $PID)."
echo "📁 Logs are being written to $LOG_FILE"
echo "🛑 To stop, run: ./stop_stripe_listener.sh"
echo ""
echo "Note: If the logs in $LOG_FILE show 'Please authenticate', run 'stripe login' interactive to refresh your token."
echo "To view the logs, run: tail -f $LOG_FILE"
