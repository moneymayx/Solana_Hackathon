import * as anchor from "@coral-xyz/anchor";
import { expect } from "chai";

const USDC_DECIMALS = 6;
const USDC_MULTIPLIER = new anchor.BN(10).pow(new anchor.BN(USDC_DECIMALS));

const randomIntBetween = (min: number, max: number): number =>
  Math.floor(Math.random() * (max - min + 1)) + min;

const computeSplit = (entryAmount: anchor.BN) => {
  const jackpot = entryAmount.mul(new anchor.BN(60)).div(new anchor.BN(100));
  const buyback = entryAmount.sub(jackpot);
  return { jackpot, buyback };
};

describe("Arithmetic fuzzing", function () {
  it("keeps split invariants for 1,200 random USDC entries", () => {
    const iterations = 1200;

    for (let i = 0; i < iterations; i++) {
      const amount = randomIntBetween(1, 1_000_000);
      const entryAmount = new anchor.BN(amount).mul(USDC_MULTIPLIER);
      const { jackpot, buyback } = computeSplit(entryAmount);

      const sum = jackpot.add(buyback);
      expect(sum.eq(entryAmount)).to.be.true;

      expect(jackpot.lte(entryAmount)).to.be.true;
      expect(buyback.gte(new anchor.BN(0))).to.be.true;
    }
  });

  it("accumulates rounding without losing tokens across repeated entries", () => {
    const iterations = 300;
    let cumulativeInput = new anchor.BN(0);
    let cumulativeProcessed = new anchor.BN(0);

    for (let i = 0; i < iterations; i++) {
      const amount = randomIntBetween(1, 100_000);
      const entryAmount = new anchor.BN(amount).mul(USDC_MULTIPLIER);
      const { jackpot, buyback } = computeSplit(entryAmount);

      cumulativeInput = cumulativeInput.add(entryAmount);
      cumulativeProcessed = cumulativeProcessed.add(jackpot).add(buyback);

      expect(cumulativeProcessed.eq(cumulativeInput)).to.be.true;
    }
  });
});

