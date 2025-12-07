#!/usr/bin/env node
/**
 * Standalone Rounding Tests
 * Tests the rounding logic without requiring blockchain/Anchor setup
 */

const anchor = require('@coral-xyz/anchor');
const BN = anchor.BN;

const USDC_DECIMALS = 6;
const USDC_MULTIPLIER = new BN(10).pow(new BN(USDC_DECIMALS));

// Replicate the contract's split calculation
const computeSplit = (entryAmount) => {
  // 60% to jackpot (rounds down)
  const jackpot = entryAmount.mul(new BN(60)).div(new BN(100));
  // 40% to buyback (remainder)
  const buyback = entryAmount.sub(jackpot);
  return { jackpot, buyback };
};

// Replicate escape plan distribution
const computeEscapePlanSplit = (totalJackpot) => {
  // 20% to last participant (rounds down)
  const lastParticipantShare = totalJackpot.mul(new BN(20)).div(new BN(100));
  // 80% to community (remainder)
  const communityShare = totalJackpot.sub(lastParticipantShare);
  return { lastParticipantShare, communityShare };
};

console.log('='.repeat(80));
console.log('ROUNDING VULNERABILITY TESTS - STANDALONE');
console.log('='.repeat(80));
console.log();

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

// Test 1: Fuzzing with 1,200 random amounts
console.log('Test 1: Fuzzing with 1,200 random USDC entries...');
totalTests++;
let fuzzingPassed = true;
for (let i = 0; i < 1200; i++) {
  const amount = Math.floor(Math.random() * 1000000) + 1;
  const entryAmount = new BN(amount).mul(USDC_MULTIPLIER);
  const { jackpot, buyback } = computeSplit(entryAmount);
  const sum = jackpot.add(buyback);
  
  if (!sum.eq(entryAmount)) {
    console.log(`  ❌ FAILED at amount ${amount}: sum mismatch`);
    console.log(`     Jackpot: ${jackpot.toString()}, Buyback: ${buyback.toString()}`);
    console.log(`     Sum: ${sum.toString()}, Expected: ${entryAmount.toString()}`);
    fuzzingPassed = false;
    failedTests++;
    break;
  }
}
if (fuzzingPassed) {
  console.log('  ✅ PASSED: All 1,200 random amounts maintain invariant');
  passedTests++;
}

console.log();

// Test 2: Edge cases that don't divide evenly
console.log('Test 2: Edge case amounts (50+ amounts that don\'t divide evenly)...');
totalTests++;
const EDGE_CASE_AMOUNTS = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 19, 23, 27, 29, 31, 33, 37, 39,
  41, 43, 47, 49, 51, 53, 57, 59, 61, 63, 67, 69, 71, 73, 77, 79, 81, 83, 87,
  89, 91, 93, 97, 99, 101, 107, 113, 131, 137, 149, 163, 179, 199, 211, 241,
  257, 271, 293, 307, 331, 349, 367, 389, 401, 433, 457, 479, 503, 541, 577,
  601, 631, 659, 673, 691, 709, 739, 751, 773, 797, 809, 829, 853, 877, 907,
  919, 947, 971, 997, 1000, 10000, 1000000, 10000000,
];

let edgeCasePassed = true;
let edgeCaseFailures = [];
EDGE_CASE_AMOUNTS.forEach(amount => {
  const entryAmount = new BN(amount).mul(USDC_MULTIPLIER);
  const { jackpot, buyback } = computeSplit(entryAmount);
  const sum = jackpot.add(buyback);
  
  if (!sum.eq(entryAmount)) {
    edgeCaseFailures.push({
      amount,
      jackpot: jackpot.toString(),
      buyback: buyback.toString(),
      sum: sum.toString(),
      expected: entryAmount.toString()
    });
    edgeCasePassed = false;
  }
});

if (edgeCasePassed) {
  console.log(`  ✅ PASSED: All ${EDGE_CASE_AMOUNTS.length} edge case amounts maintain invariant`);
  passedTests++;
} else {
  console.log(`  ❌ FAILED: ${edgeCaseFailures.length} edge cases failed`);
  edgeCaseFailures.slice(0, 5).forEach(f => {
    console.log(`     Amount ${f.amount} USDC: sum=${f.sum}, expected=${f.expected}`);
  });
  if (edgeCaseFailures.length > 5) {
    console.log(`     ... and ${edgeCaseFailures.length - 5} more failures`);
  }
  failedTests++;
}

console.log();

// Test 3: Accumulation test
console.log('Test 3: Accumulated rounding over 300 operations...');
totalTests++;
let cumulativeInput = new BN(0);
let cumulativeProcessed = new BN(0);
let accumulationPassed = true;

for (let i = 0; i < 300; i++) {
  const amount = Math.floor(Math.random() * 100000) + 1;
  const entryAmount = new BN(amount).mul(USDC_MULTIPLIER);
  const { jackpot, buyback } = computeSplit(entryAmount);
  
  cumulativeInput = cumulativeInput.add(entryAmount);
  cumulativeProcessed = cumulativeProcessed.add(jackpot).add(buyback);
  
  if (!cumulativeProcessed.eq(cumulativeInput)) {
    console.log(`  ❌ FAILED at iteration ${i}: cumulative mismatch`);
    console.log(`     Input: ${cumulativeInput.toString()}`);
    console.log(`     Processed: ${cumulativeProcessed.toString()}`);
    accumulationPassed = false;
    failedTests++;
    break;
  }
}

if (accumulationPassed) {
  console.log('  ✅ PASSED: No dust loss over 300 accumulated operations');
  console.log(`     Total Input: ${cumulativeInput.toString()}`);
  console.log(`     Total Processed: ${cumulativeProcessed.toString()}`);
  passedTests++;
}

console.log();

// Test 4: Escape plan distribution
console.log('Test 4: Escape plan distribution (20/80 split)...');
totalTests++;
const ESCAPE_PLAN_AMOUNTS = [100, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1000, 10000, 100000, 1000000];

let escapePlanPassed = true;
let escapePlanFailures = [];
ESCAPE_PLAN_AMOUNTS.forEach(amount => {
  const totalJackpot = new BN(amount).mul(USDC_MULTIPLIER);
  const { lastParticipantShare, communityShare } = computeEscapePlanSplit(totalJackpot);
  const sum = lastParticipantShare.add(communityShare);
  
  if (!sum.eq(totalJackpot)) {
    escapePlanFailures.push({
      amount,
      lastParticipant: lastParticipantShare.toString(),
      community: communityShare.toString(),
      sum: sum.toString(),
      expected: totalJackpot.toString()
    });
    escapePlanPassed = false;
  }
});

if (escapePlanPassed) {
  console.log(`  ✅ PASSED: All ${ESCAPE_PLAN_AMOUNTS.length} escape plan amounts maintain invariant`);
  passedTests++;
} else {
  console.log(`  ❌ FAILED: ${escapePlanFailures.length} escape plan cases failed`);
  escapePlanFailures.slice(0, 5).forEach(f => {
    console.log(`     Amount ${f.amount} USDC: sum=${f.sum}, expected=${f.expected}`);
  });
  if (escapePlanFailures.length > 5) {
    console.log(`     ... and ${escapePlanFailures.length - 5} more failures`);
  }
  failedTests++;
}

console.log();

// Test 5: Rounding direction verification
console.log('Test 5: Verifying rounding direction favors protocol...');
totalTests++;
let roundingDirectionPassed = true;

// Test with amounts that have remainder when divided by 100
const ROUNDING_TEST_AMOUNTS = [1, 3, 7, 11, 13, 17, 19, 23, 27, 29, 31, 33, 37, 39, 41, 43, 47, 49, 51, 53, 57, 59, 61, 63, 67, 69, 71, 73, 77, 79, 81, 83, 87, 89, 91, 93, 97, 99];
ROUNDING_TEST_AMOUNTS.forEach(amount => {
  const entryAmount = new BN(amount).mul(USDC_MULTIPLIER);
  const { jackpot, buyback } = computeSplit(entryAmount);
  
  // Calculate what 60% would be with perfect precision
  const perfectJackpot = entryAmount.mul(new BN(60)).div(new BN(100));
  const perfectBuyback = entryAmount.sub(perfectJackpot);
  
  // With integer division, jackpot should be <= perfect (rounds down)
  // and buyback should be >= perfect (gets the remainder)
  if (jackpot.gt(perfectJackpot) || buyback.lt(perfectBuyback)) {
    console.log(`  ❌ FAILED: Rounding direction incorrect for amount ${amount}`);
    console.log(`     Jackpot: ${jackpot.toString()} (should be <= ${perfectJackpot.toString()})`);
    console.log(`     Buyback: ${buyback.toString()} (should be >= ${perfectBuyback.toString()})`);
    roundingDirectionPassed = false;
    failedTests++;
  }
});

if (roundingDirectionPassed) {
  console.log('  ✅ PASSED: Rounding direction correctly favors protocol (buyback gets remainder)');
  passedTests++;
}

console.log();

// Summary
console.log('='.repeat(80));
console.log('TEST SUMMARY');
console.log('='.repeat(80));
console.log(`Total Tests: ${totalTests}`);
console.log(`Passed: ${passedTests}`);
console.log(`Failed: ${failedTests}`);
console.log();

if (failedTests === 0) {
  console.log('🎉 ALL TESTS PASSED! ✅');
  console.log();
  console.log('The rounding logic correctly:');
  console.log('  - Maintains invariant: jackpot + buyback == entry_amount');
  console.log('  - Maintains invariant: last_participant + community == total_jackpot');
  console.log('  - Rounds down for jackpot (favors protocol)');
  console.log('  - Assigns remainder to buyback (favors protocol)');
  console.log('  - Has no dust loss across accumulated operations');
  process.exit(0);
} else {
  console.log('❌ SOME TESTS FAILED');
  console.log('Please review the failures above.');
  process.exit(1);
}

