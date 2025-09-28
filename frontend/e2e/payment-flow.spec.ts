import { test, expect } from '@playwright/test';

test.describe('Payment Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to payment tab
    await page.getByRole('button', { name: /payment/i }).click();
  });

  test('should display payment flow elements', async ({ page }) => {
    // Check main elements are present
    await expect(page.getByText('Purchase bounty Entry')).toBeVisible();
    await expect(page.getByText('Payment Method')).toBeVisible();
    await expect(page.getByText('Credit Card')).toBeVisible();
    await expect(page.getByText('Wallet')).toBeVisible();
    await expect(page.getByText('Amount (USD)')).toBeVisible();
  });

  test('should show wallet connection prompt when not connected', async ({ page }) => {
    // Check wallet connection prompt
    await expect(page.getByText('Please connect your wallet to make a payment')).toBeVisible();
  });

  test('should allow selecting payment method', async ({ page }) => {
    // Check initial state - fiat should be selected
    const fiatButton = page.getByRole('button', { name: /Credit Card/i });
    const walletButton = page.getByRole('button', { name: /Wallet/i });
    
    await expect(fiatButton).toHaveClass(/bg-gradient-to-r.*from-purple-500.*to-pink-500/);
    await expect(walletButton).toHaveClass(/bg-gray-700/);
    
    // Click wallet button
    await walletButton.click();
    
    // Check state changed
    await expect(walletButton).toHaveClass(/bg-gradient-to-r.*from-purple-500.*to-pink-500/);
    await expect(fiatButton).toHaveClass(/bg-gray-700/);
  });

  test('should allow selecting amount from predefined options', async ({ page }) => {
    const amountButtons = [5, 10, 25, 50, 100, 500];
    
    for (const amount of amountButtons) {
      const button = page.getByRole('button', { name: `$${amount}` });
      await button.click();
      await expect(button).toHaveClass(/bg-gradient-to-r.*from-purple-500.*to-pink-500/);
    }
  });

  test('should allow custom amount input', async ({ page }) => {
    const customInput = page.getByPlaceholder('Custom amount');
    await customInput.fill('75');
    await expect(customInput).toHaveValue(75);
  });

  test('should fetch quote when fiat payment is selected', async ({ page }) => {
    // Mock quote API
    await page.route('**/api/moonpay/quote*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          quote: {
            baseCurrencyAmount: 10,
            quoteCurrencyAmount: 0.05,
            quoteCurrencyPrice: 200,
            feeAmount: 0.5,
            networkFeeAmount: 0.1,
            totalAmount: 10.6
          }
        })
      });
    });

    // Wait for quote to be fetched
    await page.waitForTimeout(1000);

    // Check that quote was fetched
    await expect(page.getByText('Payment Summary')).toBeVisible();
  });

  test('should display payment summary when quote is available', async ({ page }) => {
    // Mock quote API
    await page.route('**/api/moonpay/quote*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          quote: {
            baseCurrencyAmount: 10,
            quoteCurrencyAmount: 0.05,
            quoteCurrencyPrice: 200,
            feeAmount: 0.5,
            networkFeeAmount: 0.1,
            totalAmount: 10.6
          }
        })
      });
    });

    await page.waitForTimeout(1000);

    // Check payment summary is displayed
    await expect(page.getByText('Payment Summary')).toBeVisible();
    await expect(page.getByText('$10.00')).toBeVisible(); // Amount
    await expect(page.getByText('0.050000 SOL')).toBeVisible(); // You'll receive
    await expect(page.getByText('$200.00/SOL')).toBeVisible(); // Rate
    await expect(page.getByText('$0.50')).toBeVisible(); // Fee
    await expect(page.getByText('$10.60')).toBeVisible(); // Total
  });

  test('should create payment when wallet is connected', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    // Mock window.open
    await page.evaluate(() => {
      (window as any).open = (url: string) => {
        console.log('Opening URL:', url);
      };
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Check that payment was created
    await expect(page.getByText('Processing Payment')).toBeVisible();
  });

  test('should show processing state during payment creation', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock delayed payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Check processing state
    await expect(page.getByText('Processing Payment')).toBeVisible();
    await expect(page.getByText('Please complete the payment in the new tab')).toBeVisible();
  });

  test('should show success state when payment is completed', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    // Mock payment status check - completed
    await page.route('**/api/moonpay/transaction/tx-123', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transaction: { status: 'completed' }
        })
      });
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Wait for success state
    await expect(page.getByText('Payment Successful!')).toBeVisible();
    await expect(page.getByText('Transaction: tx-123')).toBeVisible();
  });

  test('should show failure state when payment fails', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API error
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Payment failed' })
      });
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Check failure state
    await expect(page.getByText('Payment Failed')).toBeVisible();
    await expect(page.getByText('Please try again')).toBeVisible();
  });

  test('should disable pay button when wallet is not connected', async ({ page }) => {
    const payButton = page.getByRole('button', { name: /Pay with Credit Card/i });
    await expect(payButton).toBeDisabled();
  });

  test('should disable pay button when amount is invalid', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Set invalid amount
    const customInput = page.getByPlaceholder('Custom amount');
    await customInput.fill('0');
    
    const payButton = page.getByRole('button', { name: /Pay with Credit Card/i });
    await expect(payButton).toBeDisabled();
  });

  test('should open payment URL when clicking open payment button', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    // Mock window.open
    let openedUrl = '';
    await page.evaluate(() => {
      (window as any).open = (url: string) => {
        (window as any).lastOpenedUrl = url;
      };
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Wait for open payment button to appear
    await expect(page.getByRole('button', { name: /Open Payment/i })).toBeVisible();

    // Click open payment button
    await page.getByRole('button', { name: /Open Payment/i }).click();

    // Check that URL was opened
    const lastOpenedUrl = await page.evaluate(() => (window as any).lastOpenedUrl);
    expect(lastOpenedUrl).toBe('https://moonpay.com/payment/123');
  });

  test('should handle payment timeout', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    // Mock payment status check - always pending
    await page.route('**/api/moonpay/transaction/tx-123', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transaction: { status: 'pending' }
        })
      });
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Wait for timeout (5 minutes + buffer)
    await page.waitForTimeout(300000 + 1000);

    // Check failure state due to timeout
    await expect(page.getByText('Payment Failed')).toBeVisible();
  });

  test('should poll payment status until completion', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
      (window as any).mockPublicKey = { toString: () => 'test-wallet-address' };
    });

    // Mock payment creation API
    await page.route('**/api/moonpay/create-payment', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          payment_url: 'https://moonpay.com/payment/123',
          transaction_id: 'tx-123',
          amount_usd: 10,
          currency_code: 'sol'
        })
      });
    });

    let statusCallCount = 0;
    // Mock payment status check - pending then completed
    await page.route('**/api/moonpay/transaction/tx-123', async route => {
      statusCallCount++;
      const status = statusCallCount === 1 ? 'pending' : 'completed';
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transaction: { status }
        })
      });
    });

    // Click pay button
    await page.getByRole('button', { name: /Pay with Credit Card/i }).click();

    // Wait for success state
    await expect(page.getByText('Payment Successful!')).toBeVisible();

    // Check that status was polled multiple times
    expect(statusCallCount).toBeGreaterThan(1);
  });
});
