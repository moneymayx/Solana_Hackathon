import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV2 } from "../target/types/billions_bounty_v2";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAssociatedTokenAddress } from "@solana/spl-token";
import { expect } from "chai";

describe("billions-bounty-v2 edge cases", () => {
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.BillionsBountyV2 as Program<BillionsBountyV2>;

  it("Rejects wrong nonce account PDA", async () => {
    const [globalPda] = PublicKey.findProgramAddressSync([Buffer.from("global")], program.programId);
    const [bountyPda] = PublicKey.findProgramAddressSync([Buffer.from("bounty"), Buffer.from([1,0,0,0,0,0,0,0])], program.programId);

    try {
      await program.methods
        .processAiDecisionV2(new anchor.BN(1), "u", "a", Array(32).fill(1), Array(64).fill(2), false, new anchor.BN(1), "session-x", new anchor.BN(Math.floor(Date.now()/1000)))
        .accounts({
          global: globalPda,
          bounty: bountyPda,
          nonceAccount: PublicKey.unique(),
          authority: Keypair.generate().publicKey,
          winner: Keypair.generate().publicKey,
          bountyPoolTokenAccount: await getAssociatedTokenAddress(PublicKey.unique(), PublicKey.unique()),
          winnerTokenAccount: await getAssociatedTokenAddress(PublicKey.unique(), PublicKey.unique()),
          bountyPoolWallet: PublicKey.unique(),
          usdcMint: PublicKey.unique(),
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .rpc();
      expect.fail("should have failed with Unauthorized/nonce mismatch");
    } catch (e) {
      expect(e.toString()).to.satisfy((s: string) => s.includes("Unauthorized") || s.includes("InvalidNonce"));
    }
  });
});


