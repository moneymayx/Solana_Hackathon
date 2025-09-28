import { test, expect } from '@playwright/test';

test.describe('bounty Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to bounty tab
    await page.getByRole('button', { name: /bounty/i }).click();
  });

  test('should display bounty statistics correctly', async ({ page }) => {
    // Mock bounty status API
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 5000,
          total_entries: 150,
          win_rate: 0.01,
          next_rollover_at: '2024-01-01T12:00:00Z'
        })
      });
    });

    await page.reload();

    // Check main stats are displayed
    await expect(page.getByText('Current Pool')).toBeVisible();
    await expect(page.getByText('$5,000.00')).toBeVisible();
    await expect(page.getByText('Total Entries')).toBeVisible();
    await expect(page.getByText('150')).toBeVisible();
    await expect(page.getByText('Win Rate')).toBeVisible();
    await expect(page.getByText('1.00%')).toBeVisible();
  });

  test('should display next rollover information when available', async ({ page }) => {
    // Mock bounty status with rollover
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 5000,
          total_entries: 150,
          win_rate: 0.01,
          next_rollover_at: '2024-01-01T12:00:00Z'
        })
      });
    });

    await page.reload();

    // Check rollover information
    await expect(page.getByText('Next Rollover')).toBeVisible();
    await expect(page.getByText(/If no winner is found/)).toBeVisible();
  });

  test('should display user history when wallet is connected', async ({ page }) => {
    // Mock wallet connection
    await page.evaluate(() => {
      (window as any).mockWalletConnected = true;
    });

    // Mock bounty status
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

    // Mock user history
    await page.route('**/api/bounty/history', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_entries: 5,
          total_spent: 50,
          wins: 1,
          last_entry: '2024-01-01T10:00:00Z'
        })
      });
    });

    await page.reload();

    // Check user stats are displayed
    await expect(page.getByText('Your Stats')).toBeVisible();
    await expect(page.getByText('5')).toBeVisible(); // Total entries
    await expect(page.getByText('$50.00')).toBeVisible(); // Total spent
    await expect(page.getByText('1')).toBeVisible(); // Wins
    await expect(page.getByText('20.00%')).toBeVisible(); // Win rate
  });

  test('should display recent winners when available', async ({ page }) => {
    // Mock bounty status with recent winners
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 5000,
          total_entries: 150,
          win_rate: 0.01,
          recent_winners: [
            {
              user_id: 1,
              prize_amount: 1000,
              won_at: '2024-01-01T10:00:00Z'
            },
            {
              user_id: 2,
              prize_amount: 500,
              won_at: '2024-01-01T09:00:00Z'
            }
          ]
        })
      });
    });

    await page.reload();

    // Check recent winners are displayed
    await expect(page.getByText('Recent Winners')).toBeVisible();
    await expect(page.getByText('User #1')).toBeVisible();
    await expect(page.getByText('User #2')).toBeVisible();
    await expect(page.getByText('$1,000.00')).toBeVisible();
    await expect(page.getByText('$500.00')).toBeVisible();
  });

  test('should display how to play instructions', async ({ page }) => {
    // Mock bounty status
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

    await page.reload();

    // Check how to play section
    await expect(page.getByText('How to Play')).toBeVisible();
    await expect(page.getByText(/Connect your Solana wallet/)).toBeVisible();
    await expect(page.getByText(/Chat with the AI guardian/)).toBeVisible();
    await expect(page.getByText(/Each message costs \$10/)).toBeVisible();
    await expect(page.getByText(/Win rate is currently/)).toBeVisible();
  });

  test('should handle loading state', async ({ page }) => {
    // Mock delayed bounty status API
    await page.route('**/api/bounty/status', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
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

    await page.reload();

    // Check loading state appears
    await expect(page.getByText('Loading bounty data...')).toBeVisible();

    // Wait for data to load
    await expect(page.getByText('Current Pool')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await page.reload();

    // Check error state appears
    await expect(page.getByText('Failed to load bounty data')).toBeVisible();
  });

  test('should update data every 5 seconds', async ({ page }) => {
    let callCount = 0;
    
    // Mock bounty status API with different responses
    await page.route('**/api/bounty/status', async route => {
      callCount++;
      const pool = 5000 + (callCount * 100); // Increase pool each call
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: pool,
          total_entries: 150,
          win_rate: 0.01
        })
      });
    });

    await page.reload();

    // Wait for initial load
    await expect(page.getByText('$5,000.00')).toBeVisible();

    // Wait for update (5 seconds + buffer)
    await page.waitForTimeout(6000);

    // Check that data was updated
    await expect(page.getByText('$5,100.00')).toBeVisible();
  });

  test('should format currency correctly', async ({ page }) => {
    // Mock bounty status with large numbers
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 1234567.89,
          total_entries: 150,
          win_rate: 0.01
        })
      });
    });

    await page.reload();

    // Check currency formatting
    await expect(page.getByText('$1,234,567.89')).toBeVisible();
  });

  test('should calculate win rate percentage correctly', async ({ page }) => {
    // Mock bounty status with low win rate
    await page.route('**/api/bounty/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          current_pool: 5000,
          total_entries: 150,
          win_rate: 0.0001 // 0.01%
        })
      });
    });

    await page.reload();

    // Check win rate formatting
    await expect(page.getByText('0.01%')).toBeVisible();
  });
});
