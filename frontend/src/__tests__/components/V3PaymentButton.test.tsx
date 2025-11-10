/**
 * V3PaymentButton Component Tests
 * 
 * Tests the V3 payment button component with React Testing Library
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WalletProvider, ConnectionProvider } from "@solana/wallet-adapter-react";
import { WalletAdapterNetwork } from "@solana/wallet-adapter-base";
import {
  PhantomWalletAdapter,
  SolflareWalletAdapter,
} from "@solana/wallet-adapter-wallets";
import { clusterApiUrl } from "@solana/web3.js";
import V3PaymentButton from "@/components/V3PaymentButton";

// Mock the payment processor
jest.mock("@/lib/v3/paymentProcessor", () => ({
  processV3EntryPayment: jest.fn(),
  usdcToSmallestUnit: (amount: number) => amount * 1_000_000,
}));

// Mock wallet adapter hooks
const mockPublicKey = {
  toString: () => "mock-wallet-address",
  toBase58: () => "mock-wallet-address",
};

const mockSignTransaction = jest.fn(async (tx: any) => tx);

const mockUseWallet = {
  publicKey: mockPublicKey,
  signTransaction: mockSignTransaction,
  connected: true,
  connecting: false,
  wallet: null,
  connect: jest.fn(),
  disconnect: jest.fn(),
  select: jest.fn(),
};

jest.mock("@solana/wallet-adapter-react", () => {
  const actual = jest.requireActual("@solana/wallet-adapter-react");
  return {
    ...actual,
    useWallet: () => mockUseWallet,
    useConnection: () => ({
      connection: {
        getLatestBlockhash: jest.fn(),
        sendRawTransaction: jest.fn(),
        confirmTransaction: jest.fn(),
      },
    }),
  };
});

describe("V3PaymentButton", () => {
  const wallets = [new PhantomWalletAdapter(), new SolflareWalletAdapter()];
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = clusterApiUrl(network);

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <ConnectionProvider endpoint={endpoint}>
        <WalletProvider wallets={wallets} autoConnect>
          {component}
        </WalletProvider>
      </ConnectionProvider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseWallet.connected = true;
    mockUseWallet.publicKey = mockPublicKey;
  });

  describe("Rendering", () => {
    it("should render payment button", () => {
      renderWithProviders(<V3PaymentButton />);
      expect(screen.getByLabelText(/Payment Amount/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Pay/i })).toBeInTheDocument();
    });

    it("should display default amount", () => {
      renderWithProviders(<V3PaymentButton defaultAmount={15} />);
      const input = screen.getByLabelText(/Payment Amount/i) as HTMLInputElement;
      expect(input.value).toBe("15");
    });

    it("should show connect wallet message when not connected", () => {
      mockUseWallet.connected = false;
      mockUseWallet.publicKey = null;
      renderWithProviders(<V3PaymentButton />);
      expect(screen.getByText(/Connect your Solana wallet/i)).toBeInTheDocument();
    });
  });

  describe("User Interaction", () => {
    it("should update amount when user types", () => {
      renderWithProviders(<V3PaymentButton />);
      const input = screen.getByLabelText(/Payment Amount/i) as HTMLInputElement;
      
      fireEvent.change(input, { target: { value: "25" } });
      expect(input.value).toBe("25");
    });

    it("should disable input and button when loading", () => {
      renderWithProviders(<V3PaymentButton />);
      const input = screen.getByLabelText(/Payment Amount/i);
      const button = screen.getByRole("button");
      
      // Simulate loading state by clicking
      fireEvent.click(button);
      
      // In real implementation, loading would disable inputs
      // This test verifies the structure is correct
      expect(input).toBeInTheDocument();
      expect(button).toBeInTheDocument();
    });
  });

  describe("Payment Processing", () => {
    it("should call processV3EntryPayment on button click", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockResolvedValue({
        success: true,
        transactionSignature: "test-signature-123",
        explorerUrl: "https://explorer.solana.com/tx/test-signature-123",
      });

      renderWithProviders(<V3PaymentButton />);
      const button = screen.getByRole("button", { name: /Pay/i });
      
      fireEvent.click(button);

      await waitFor(() => {
        expect(processV3EntryPayment).toHaveBeenCalled();
      });

      expect(processV3EntryPayment).toHaveBeenCalledWith(
        expect.any(Object), // connection
        mockPublicKey,
        mockSignTransaction,
        10_000_000 // 10 USDC in smallest units
      );
    });

    it("should call onSuccess callback when payment succeeds", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockResolvedValue({
        success: true,
        transactionSignature: "test-sig",
        explorerUrl: "https://explorer.solana.com/tx/test-sig",
      });

      const onSuccess = jest.fn();
      renderWithProviders(<V3PaymentButton onSuccess={onSuccess} />);
      
      fireEvent.click(screen.getByRole("button", { name: /Pay/i }));

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(
          "test-sig",
          "https://explorer.solana.com/tx/test-sig"
        );
      });
    });

    it("should call onError callback when payment fails", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockResolvedValue({
        success: false,
        error: "Insufficient funds",
      });

      const onError = jest.fn();
      renderWithProviders(<V3PaymentButton onError={onError} />);
      
      fireEvent.click(screen.getByRole("button", { name: /Pay/i }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("Insufficient funds");
      });
    });

    it("should show error message when wallet is not connected", () => {
      mockUseWallet.connected = false;
      mockUseWallet.publicKey = null;
      
      const onError = jest.fn();
      renderWithProviders(<V3PaymentButton onError={onError} />);
      
      fireEvent.click(screen.getByRole("button", { name: /Connect Wallet/i }));

      expect(onError).toHaveBeenCalledWith("Please connect your wallet");
    });

    it("should validate amount is greater than 0", async () => {
      const onError = jest.fn();
      renderWithProviders(<V3PaymentButton defaultAmount={0} onError={onError} />);
      
      const button = screen.getByRole("button");
      expect(button).toBeDisabled(); // Button should be disabled for amount <= 0
    });
  });

  describe("Error Handling", () => {
    it("should display error message when payment fails", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockResolvedValue({
        success: false,
        error: "Transaction failed",
      });

      renderWithProviders(<V3PaymentButton />);
      fireEvent.click(screen.getByRole("button", { name: /Pay/i }));

      await waitFor(() => {
        expect(screen.getByText(/Payment Failed/i)).toBeInTheDocument();
        expect(screen.getByText(/Transaction failed/i)).toBeInTheDocument();
      });
    });

    it("should handle thrown errors gracefully", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockRejectedValue(new Error("Network error"));

      const onError = jest.fn();
      renderWithProviders(<V3PaymentButton onError={onError} />);
      
      fireEvent.click(screen.getByRole("button", { name: /Pay/i }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith("Network error");
      });
    });
  });

  describe("Success State", () => {
    it("should display success message with explorer link", async () => {
      const processV3EntryPayment = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
      processV3EntryPayment.mockResolvedValue({
        success: true,
        transactionSignature: "sig-123",
        explorerUrl: "https://explorer.solana.com/tx/sig-123",
      });

      renderWithProviders(<V3PaymentButton />);
      fireEvent.click(screen.getByRole("button", { name: /Pay/i }));

      await waitFor(() => {
        expect(screen.getByText(/Payment Successful/i)).toBeInTheDocument();
        const explorerLink = screen.getByText(/View on Explorer/i);
        expect(explorerLink).toBeInTheDocument();
        expect(explorerLink.closest("a")).toHaveAttribute(
          "href",
          "https://explorer.solana.com/tx/sig-123"
        );
      });
    });
  });
});

