#!/bin/bash
# Check balances of all wallets we have authority for
# Logs progress to avoid hanging

LOG_FILE="wallet_balance_check.log"
echo "Starting wallet balance check at $(date)" | tee "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

cd "$(dirname "$0")/.."

echo "[$(date)] 1. Checking Solana CLI default wallet..." | tee -a "$LOG_FILE"
SOLANA_KEYPAIR=$(solana config get 2>/dev/null | grep "Keypair Path" | awk '{print $3}' || echo "")
if [ -n "$SOLANA_KEYPAIR" ] && [ -f "$SOLANA_KEYPAIR" ]; then
    PUBKEY=$(solana-keygen pubkey "$SOLANA_KEYPAIR" 2>/dev/null || echo "invalid")
    if [ "$PUBKEY" != "invalid" ]; then
        BALANCE=$(solana balance "$PUBKEY" --url devnet 2>/dev/null | awk '{print $1}' || echo "error")
        echo "  ✅ Default wallet: $PUBKEY" | tee -a "$LOG_FILE"
        echo "     Balance: $BALANCE" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi
fi

echo "[$(date)] 2. Checking program keypair files..." | tee -a "$LOG_FILE"
COUNT=0
TOTAL_SOL=0
for KEYPAIR in $(find . -name "*-keypair.json" -type f 2>/dev/null | grep -v node_modules | grep -v ".git" | head -20); do
    COUNT=$((COUNT + 1))
    echo "[$(date)]   Checking $COUNT: $KEYPAIR" | tee -a "$LOG_FILE"
    PUBKEY=$(solana-keygen pubkey "$KEYPAIR" 2>/dev/null || echo "invalid")
    if [ "$PUBKEY" != "invalid" ]; then
        BALANCE=$(solana balance "$PUBKEY" --url devnet 2>/dev/null | awk '{print $1}' || echo "0 SOL")
        BALANCE_NUM=$(echo "$BALANCE" | sed 's/ SOL//' | awk '{print $1}')
        if (( $(echo "$BALANCE_NUM > 0" | bc -l 2>/dev/null || echo 0) )); then
            echo "     ✅ Program ID: $PUBKEY" | tee -a "$LOG_FILE"
            echo "        Balance: $BALANCE" | tee -a "$LOG_FILE"
            TOTAL_SOL=$(echo "$TOTAL_SOL + $BALANCE_NUM" | bc -l 2>/dev/null || echo "$TOTAL_SOL")
        else
            echo "     ⚪ Balance: $BALANCE (skipping)" | tee -a "$LOG_FILE"
        fi
    else
        echo "     ❌ Invalid keypair" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
done

echo "[$(date)] 3. Checking Kora wallet (if configured)..." | tee -a "$LOG_FILE"
if [ -f "config/kora_keypair_info.txt" ]; then
    KORA_PUBKEY=$(grep "Public Key" config/kora_keypair_info.txt | awk -F': ' '{print $2}' || echo "")
    if [ -n "$KORA_PUBKEY" ]; then
        BALANCE=$(solana balance "$KORA_PUBKEY" --url devnet 2>/dev/null | awk '{print $1}' || echo "error")
        echo "  ✅ Kora wallet: $KORA_PUBKEY" | tee -a "$LOG_FILE"
        echo "     Balance: $BALANCE" | tee -a "$LOG_FILE"
        BALANCE_NUM=$(echo "$BALANCE" | sed 's/ SOL//' | awk '{print $1}')
        if (( $(echo "$BALANCE_NUM > 0" | bc -l 2>/dev/null || echo 0) )); then
            TOTAL_SOL=$(echo "$TOTAL_SOL + $BALANCE_NUM" | bc -l 2>/dev/null || echo "$TOTAL_SOL")
        fi
        echo "" | tee -a "$LOG_FILE"
    fi
fi

echo "[$(date)] 4. Checking known wallet addresses from config..." | tee -a "$LOG_FILE"
KNOWN_WALLETS=(
    "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"  # Jackpot wallet
    "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D"  # Operational wallet
    "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya"  # Buyback wallet
    "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"  # Staking wallet
)

for WALLET in "${KNOWN_WALLETS[@]}"; do
    echo "[$(date)]   Checking: $WALLET" | tee -a "$LOG_FILE"
    BALANCE=$(timeout 5 solana balance "$WALLET" --url devnet 2>/dev/null | awk '{print $1}' || echo "timeout/error")
    BALANCE_NUM=$(echo "$BALANCE" | sed 's/ SOL//' | awk '{print $1}')
    if [ "$BALANCE" != "timeout/error" ] && [ -n "$BALANCE_NUM" ]; then
        echo "     Balance: $BALANCE" | tee -a "$LOG_FILE"
        if (( $(echo "$BALANCE_NUM > 0" | bc -l 2>/dev/null || echo 0) )); then
            TOTAL_SOL=$(echo "$TOTAL_SOL + $BALANCE_NUM" | bc -l 2>/dev/null || echo "$TOTAL_SOL")
        fi
    else
        echo "     ⚠️  Could not check (timeout or error)" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
done

echo "[$(date)] Summary:" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
DEFAULT_BALANCE=$(solana balance --url devnet 2>/dev/null | awk '{print $1}' || echo "unknown")
echo "Default wallet balance: $DEFAULT_BALANCE" | tee -a "$LOG_FILE"
echo "Total SOL found in other wallets: $TOTAL_SOL SOL" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ Check complete at $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE"

