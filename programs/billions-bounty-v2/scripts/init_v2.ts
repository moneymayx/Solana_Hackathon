import * as anchor from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import * as fs from "fs";

(async () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const programId = new PublicKey(process.env.LOTTERY_PROGRAM_ID_V2 || "4ChHkYCu5Q8KpBh1pPEx5KgKTQGySikhvzhi3KYrUMuW");
  let idl: any = await (anchor as any).Program.fetchIdl(programId, provider);
  if (!idl) {
    const localPath = `${__dirname}/../target/idl/billions_bounty_v2.json`;
    if (!fs.existsSync(localPath)) throw new Error("IDL not found (remote/local)");
    const raw = fs.readFileSync(localPath, "utf8");
    if (!raw) throw new Error("Local IDL file is empty");
    idl = JSON.parse(raw);
  }
  const program = new (anchor as any).Program(idl, programId, provider);

  const bountyPoolWallet = new PublicKey(process.env.BOUNTY_POOL_WALLET!);
  const operationalWallet = new PublicKey(process.env.OPERATIONAL_WALLET!);
  const buybackWallet = new PublicKey(process.env.BUYBACK_WALLET!);
  const stakingWallet = new PublicKey(process.env.STAKING_WALLET!);
  const usdcMint = new PublicKey(process.env.USDC_MINT || PublicKey.default.toBase58());

  const [globalPda] = PublicKey.findProgramAddressSync([Buffer.from("global")], program.programId);
  const [bountyPda] = PublicKey.findProgramAddressSync([Buffer.from("bounty"), Buffer.from([1,0,0,0,0,0,0,0])], program.programId);

  console.log("Initializing lottery (v2)...", globalPda.toBase58());
  await program.methods
    .initializeLottery(new anchor.BN(1_000_000_000), new anchor.BN(10_000_000), bountyPoolWallet, operationalWallet, buybackWallet, stakingWallet)
    .accounts({
      global: globalPda,
      authority: provider.wallet.publicKey,
      bountyPoolWallet,
      operationalWallet,
      buybackWallet,
      stakingWallet,
      bountyPoolTokenAccount: PublicKey.default,
      usdcMint,
      tokenProgram: (anchor as any).utils.token.TOKEN_PROGRAM_ID,
      associatedTokenProgram: (anchor as any).utils.token.ASSOCIATED_PROGRAM_ID,
      systemProgram: anchor.web3.SystemProgram.programId,
    })
    .rpc();

  console.log("Initializing bounty 1...", bountyPda.toBase58());
  await program.methods
    .initializeBounty(new anchor.BN(1), new anchor.BN(10_000_000))
    .accounts({
      bounty: bountyPda,
      global: globalPda,
      authority: provider.wallet.publicKey,
      systemProgram: anchor.web3.SystemProgram.programId,
    })
    .rpc();

  console.log("Done.");
})();
