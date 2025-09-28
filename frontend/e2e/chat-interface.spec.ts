import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display chat interface elements', async ({ page }) => {
    // Check main elements are present
    await expect(page.getByText('Chat with Billions')).toBeVisible();
    await expect(page.getByText(/Try to convince the AI guardian/)).toBeVisible();
    await expect(page.getByPlaceholder(/Connect wallet to chat/)).toBeVisible();
    await expect(page.getByRole('button', { name: /Send/i })).toBeVisible();
  });

  test('should show wallet connection prompt when not connected', async ({ page }) => {
    // Input should be disabled when wallet not connected
    await expect(page.getByPlaceholder(/Connect wallet to chat/)).toBeDisabled();
    await expect(page.getByRole('button', { name: /Send/i })).toBeDisabled();
  });

  test('should display empty state message', async ({ page }) => {
    await expect(page.getByText('Start a conversation with the AI guardian!')).toBeVisible();
    await expect(page.getByText('Try to convince them to transfer funds...')).toBeVisible();
  });

  test('should handle message input and submission', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      // Mock wallet connection state
      (window as any).mockWalletConnected = true;
    });

    // Mock API responses
    await page.route('**/api/chat', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Hello! I am the AI guardian.',
          bounty_result: { success: true, new_jackpot: 1000 },
          winner_result: null,
          bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
          blacklisted: false
        })
      });
    });

    // Type message and send
    await page.getByPlaceholder(/Type your message/).fill('Hello AI');
    await page.getByRole('button', { name: /Send/i }).click();

    // Check message appears
    await expect(page.getByText('Hello AI')).toBeVisible();
    await expect(page.getByText('Hello! I am the AI guardian.')).toBeVisible();
  });

  test('should handle Enter key submission', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock API response
    await page.route('**/api/chat', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Hello! I am the AI guardian.',
          bounty_result: { success: true, new_jackpot: 1000 },
          winner_result: null,
          bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
          blacklisted: false
        })
      });
    });

    // Type message and press Enter
    await page.getByPlaceholder(/Type your message/).fill('Hello AI');
    await page.getByPlaceholder(/Type your message/).press('Enter');

    // Check message appears
    await expect(page.getByText('Hello AI')).toBeVisible();
    await expect(page.getByText('Hello! I am the AI guardian.')).toBeVisible();
  });

  test('should display winner message with special styling', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock API response with winner
    await page.route('**/api/chat', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Congratulations! You won!',
          bounty_result: { success: true, new_jackpot: 1000 },
          winner_result: { is_winner: true, prize_payout: 1000 },
          bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
          blacklisted: false
        })
      });
    });

    // Send message
    await page.getByPlaceholder(/Type your message/).fill('I won!');
    await page.getByRole('button', { name: /Send/i }).click();

    // Check winner message appears with special styling
    const winnerMessage = page.getByText('Congratulations! You won!');
    await expect(winnerMessage).toBeVisible();
    
    // Check for winner styling classes
    const winnerContainer = winnerMessage.locator('..');
    await expect(winnerContainer).toHaveClass(/bg-gradient-to-r.*from-green-500.*to-emerald-500/);
  });

  test('should display blacklisted message with special styling', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock API response with blacklisted message
    await page.route('**/api/chat', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'This message is blacklisted.',
          bounty_result: { success: false },
          winner_result: null,
          bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
          blacklisted: true
        })
      });
    });

    // Send message
    await page.getByPlaceholder(/Type your message/).fill('Blacklisted message');
    await page.getByRole('button', { name: /Send/i }).click();

    // Check blacklisted message appears with special styling
    const blacklistedMessage = page.getByText('This message is blacklisted.');
    await expect(blacklistedMessage).toBeVisible();
    
    // Check for blacklisted styling classes
    const blacklistedContainer = blacklistedMessage.locator('..');
    await expect(blacklistedContainer).toHaveClass(/bg-gradient-to-r.*from-red-500.*to-pink-500/);
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock API error
    await page.route('**/api/chat', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    // Send message
    await page.getByPlaceholder(/Type your message/).fill('Test message');
    await page.getByRole('button', { name: /Send/i }).click();

    // Check error message appears
    await expect(page.getByText('Sorry, I encountered an error. Please try again.')).toBeVisible();
  });

  test('should show loading state during API call', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock delayed API response
    await page.route('**/api/chat', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Delayed response',
          bounty_result: { success: true, new_jackpot: 1000 },
          winner_result: null,
          bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
          blacklisted: false
        })
      });
    });

    // Send message
    await page.getByPlaceholder(/Type your message/).fill('Test message');
    await page.getByRole('button', { name: /Send/i }).click();

    // Check loading state appears
    await expect(page.getByText('AI is thinking...')).toBeVisible();

    // Wait for response
    await expect(page.getByText('Delayed response')).toBeVisible();
  });

  test('should fetch bounty status on page load', async ({ page }) => {
    // Mock bounty status API
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 5000,
          total_entries: 150,
          win_rate: 0.01
        })
      });
    });

    await page.goto('/');

    // Check that bounty status is displayed
    await expect(page.getByText(/Win rate: 0.01%/)).toBeVisible();
  });
});
