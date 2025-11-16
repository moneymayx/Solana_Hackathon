// Manual IDL generator for billions-bounty-v3
// This generates a minimal but complete IDL from the program structure
// Following the same pattern as v2

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Helper to calculate Anchor discriminator
function calculateDiscriminator(instructionName) {
  const seed = `global:${instructionName}`;
  const hash = crypto.createHash('sha256').update(seed).digest();
  return Array.from(hash.slice(0, 8));
}

// Helper to calculate account discriminator
function calculateAccountDiscriminator(accountName) {
  const seed = `account:${accountName}`;
  const hash = crypto.createHash('sha256').update(seed).digest();
  return Array.from(hash.slice(0, 8));
}

const idl = {
  "address": "ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb",
  "metadata": {
    "name": "billions_bounty_v3",
    "version": "0.3.0",
    "spec": "0.1.0"
  },
  "instructions": [
    {
      "name": "initializeLottery",
      "discriminator": calculateDiscriminator("initialize_lottery"),
      "accounts": [
        { "name": "lottery", "isMut": true, "isSigner": false },
        { "name": "authority", "isMut": true, "isSigner": true },
        { "name": "jackpotTokenAccount", "isMut": false, "isSigner": false },
        { "name": "usdcMint", "isMut": false, "isSigner": false },
        { "name": "tokenProgram", "isMut": false, "isSigner": false },
        { "name": "systemProgram", "isMut": false, "isSigner": false }
      ],
      "args": [
        { "name": "researchFundFloor", "type": "u64" },
        { "name": "researchFee", "type": "u64" },
        { "name": "jackpotWallet", "type": "pubkey" },
        { "name": "backendAuthority", "type": "pubkey" }
      ]
    },
    {
      "name": "processEntryPayment",
      "discriminator": calculateDiscriminator("process_entry_payment"),
      "accounts": [
        { "name": "lottery", "isMut": true, "isSigner": false },
        { "name": "entry", "isMut": true, "isSigner": false },
        { "name": "user", "isMut": true, "isSigner": true },
        { "name": "userWallet", "isMut": false, "isSigner": false },
        { "name": "userTokenAccount", "isMut": true, "isSigner": false },
        { "name": "jackpotTokenAccount", "isMut": true, "isSigner": false },
        { "name": "buybackWallet", "isMut": false, "isSigner": false },
        { "name": "buybackTokenAccount", "isMut": true, "isSigner": false },
        { "name": "usdcMint", "isMut": false, "isSigner": false },
        { "name": "tokenProgram", "isMut": false, "isSigner": false },
        { "name": "associatedTokenProgram", "isMut": false, "isSigner": false },
        { "name": "systemProgram", "isMut": false, "isSigner": false }
      ],
      "args": [
        { "name": "entryAmount", "type": "u64" },
        { "name": "userWallet", "type": "pubkey" },
        { "name": "entryNonce", "type": "u64" }
      ]
    },
    {
      "name": "processAiDecision",
      "discriminator": calculateDiscriminator("process_ai_decision"),
      "accounts": [
        { "name": "lottery", "isMut": true, "isSigner": false },
        { "name": "backendAuthority", "isMut": false, "isSigner": true },
        { "name": "winner", "isMut": false, "isSigner": false },
        { "name": "winnerTokenAccount", "isMut": true, "isSigner": false },
        { "name": "jackpotTokenAccount", "isMut": true, "isSigner": false },
        { "name": "tokenProgram", "isMut": false, "isSigner": false },
        { "name": "systemProgram", "isMut": false, "isSigner": false }
      ],
      "args": [
        { "name": "userMessage", "type": "string" },
        { "name": "aiResponse", "type": "string" },
        { "name": "decisionHash", "type": { "array": ["u8", 32] } },
        { "name": "signature", "type": { "array": ["u8", 64] } },
        { "name": "isSuccessfulJailbreak", "type": "bool" },
        { "name": "userId", "type": "u64" },
        { "name": "sessionId", "type": "string" },
        { "name": "timestamp", "type": "i64" }
      ]
    },
    {
      "name": "emergencyRecovery",
      "discriminator": calculateDiscriminator("emergency_recovery"),
      "accounts": [
        { "name": "lottery", "isMut": true, "isSigner": false },
        { "name": "authority", "isMut": false, "isSigner": true },
        { "name": "jackpotTokenAccount", "isMut": true, "isSigner": false },
        { "name": "authorityTokenAccount", "isMut": true, "isSigner": false },
        { "name": "tokenProgram", "isMut": false, "isSigner": false },
        { "name": "systemProgram", "isMut": false, "isSigner": false }
      ],
      "args": [
        { "name": "amount", "type": "u64" }
      ]
    },
    {
      "name": "executeTimeEscapePlan",
      "discriminator": calculateDiscriminator("execute_time_escape_plan"),
      "accounts": [
        { "name": "lottery", "isMut": true, "isSigner": false },
        { "name": "authority", "isMut": false, "isSigner": true },
        { "name": "jackpotTokenAccount", "isMut": true, "isSigner": false },
        { "name": "tokenProgram", "isMut": false, "isSigner": false },
        { "name": "systemProgram", "isMut": false, "isSigner": false }
      ],
      "args": [
        { "name": "lastParticipant", "type": "pubkey" },
        { "name": "participantList", "type": { "vec": "pubkey" } }
      ]
    }
  ],
  "types": [
    {
      "name": "lottery",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "authority", "type": "pubkey" },
          { "name": "jackpotWallet", "type": "pubkey" },
          { "name": "backendAuthority", "type": "pubkey" },
          { "name": "researchFundFloor", "type": "u64" },
          { "name": "researchFee", "type": "u64" },
          { "name": "currentJackpot", "type": "u64" },
          { "name": "totalEntries", "type": "u64" },
          { "name": "isActive", "type": "bool" },
          { "name": "isProcessing", "type": "bool" },
          { "name": "lastRollover", "type": "i64" },
          { "name": "nextRollover", "type": "i64" },
          { "name": "researchFundContribution", "type": "u64" },
          { "name": "operationalFee", "type": "u64" },
          { "name": "lastRecoveryTime", "type": "i64" }
        ]
      }
    },
    {
      "name": "entry",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "userWallet", "type": "pubkey" },
          { "name": "amountPaid", "type": "u64" },
          { "name": "researchContribution", "type": "u64" },
          { "name": "operationalFee", "type": "u64" },
          { "name": "timestamp", "type": "i64" },
          { "name": "isProcessed", "type": "bool" }
        ]
      }
    },
    {
      "name": "lotteryInitialized",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "authority", "type": "pubkey" },
          { "name": "jackpotWallet", "type": "pubkey" },
          { "name": "backendAuthority", "type": "pubkey" },
          { "name": "researchFundFloor", "type": "u64" },
          { "name": "researchFee", "type": "u64" }
        ]
      }
    },
    {
      "name": "entryProcessed",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "userWallet", "type": "pubkey" },
          { "name": "amount", "type": "u64" },
          { "name": "researchContribution", "type": "u64" },
          { "name": "operationalFee", "type": "u64" },
          { "name": "newJackpot", "type": "u64" }
        ]
      }
    },
    {
      "name": "winnerSelected",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "winner", "type": "pubkey" },
          { "name": "amount", "type": "u64" },
          { "name": "userId", "type": "u64" },
          { "name": "sessionId", "type": "string" },
          { "name": "userMessage", "type": "string" },
          { "name": "aiResponse", "type": "string" }
        ]
      }
    },
    {
      "name": "emergencyRecoveryEvent",
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "authority", "type": "pubkey" },
          { "name": "amount", "type": "u64" },
          { "name": "timestamp", "type": "i64" },
          { "name": "maxRecoveryAllowed", "type": "u64" }
        ]
      }
    }
  ],
  "accounts": [
    {
      "name": "lottery",
      "discriminator": calculateAccountDiscriminator("lottery"),
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "authority", "type": "pubkey" },
          { "name": "jackpotWallet", "type": "pubkey" },
          { "name": "backendAuthority", "type": "pubkey" },
          { "name": "researchFundFloor", "type": "u64" },
          { "name": "researchFee", "type": "u64" },
          { "name": "researchFundContribution", "type": "u64" },
          { "name": "operationalFee", "type": "u64" },
          { "name": "currentJackpot", "type": "u64" },
          { "name": "totalEntries", "type": "u64" },
          { "name": "isActive", "type": "bool" },
          { "name": "isProcessing", "type": "bool" },
          { "name": "lastRollover", "type": "i64" },
          { "name": "nextRollover", "type": "i64" },
          { "name": "lastRecoveryTime", "type": "i64" }
        ]
      }
    },
    {
      "name": "entry",
      "discriminator": calculateAccountDiscriminator("entry"),
      "type": {
        "kind": "struct",
        "fields": [
          { "name": "userWallet", "type": "pubkey" },
          { "name": "amountPaid", "type": "u64" },
          { "name": "researchContribution", "type": "u64" },
          { "name": "operationalFee", "type": "u64" },
          { "name": "timestamp", "type": "i64" },
          { "name": "isProcessed", "type": "bool" }
        ]
      }
    }
  ],
  "events": [
    {
      "name": "lotteryInitialized",
      "discriminator": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
      "name": "entryProcessed",
      "discriminator": [9, 10, 11, 12, 13, 14, 15, 16]
    },
    {
      "name": "winnerSelected",
      "discriminator": [17, 18, 19, 20, 21, 22, 23, 24]
    },
    {
      "name": "emergencyRecoveryEvent",
      "discriminator": [25, 26, 27, 28, 29, 30, 31, 32]
    }
  ],
  "errors": [
    { "code": 6000, "name": "Unauthorized", "msg": "Unauthorized" },
    { "code": 6001, "name": "LotteryInactive", "msg": "Lottery is not active" },
    { "code": 6002, "name": "InsufficientFunds", "msg": "Insufficient funds" },
    { "code": 6003, "name": "InvalidInput", "msg": "Invalid input" },
    { "code": 6004, "name": "InvalidSignature", "msg": "Invalid signature format" },
    { "code": 6005, "name": "InvalidDecisionHash", "msg": "Decision hash mismatch" },
    { "code": 6006, "name": "InsufficientInitialFunding", "msg": "Insufficient initial funding" },
    { "code": 6007, "name": "InsufficientPayment", "msg": "Insufficient payment" },
    { "code": 6008, "name": "InputTooLong", "msg": "Input exceeds maximum length" },
    { "code": 6009, "name": "InvalidSessionId", "msg": "Invalid session ID format" },
    { "code": 6010, "name": "InvalidTimestamp", "msg": "Invalid timestamp" },
    { "code": 6011, "name": "TimestampOutOfRange", "msg": "Timestamp out of acceptable range" },
    { "code": 6012, "name": "UnauthorizedBackend", "msg": "Unauthorized backend authority" },
    { "code": 6013, "name": "ReentrancyDetected", "msg": "Reentrancy detected" },
    { "code": 6014, "name": "RecoveryCooldownActive", "msg": "Recovery cooldown period active" },
    { "code": 6015, "name": "RecoveryAmountExceedsLimit", "msg": "Recovery amount exceeds maximum limit" },
    { "code": 6016, "name": "InvalidPubkey", "msg": "Invalid public key" }
  ]
};

// Write to target/idl (Anchor expects this name with underscore)
const outputPath1 = path.join(__dirname, '../target/idl/billions_bounty_v_3.json');
const outputPath2 = path.join(__dirname, '../target/idl/billions_bounty_v3.json');
fs.mkdirSync(path.dirname(outputPath1), { recursive: true });
fs.writeFileSync(outputPath1, JSON.stringify(idl, null, 2));
fs.writeFileSync(outputPath2, JSON.stringify(idl, null, 2));

console.log(`✅ IDL written to ${outputPath1}`);
console.log(`✅ IDL written to ${outputPath2}`);
console.log(`   Size: ${JSON.stringify(idl).length} bytes`);

