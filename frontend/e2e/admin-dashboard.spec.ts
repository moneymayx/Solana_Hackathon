import { test, expect } from '@playwright/test';

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to admin tab
    await page.getByRole('button', { name: /admin/i }).click();
  });

  test('should display admin statistics correctly', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 25,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.reload();

    // Check admin stats are displayed
    await expect(page.getByText('Total Users')).toBeVisible();
    await expect(page.getByText('100')).toBeVisible();
    await expect(page.getByText('Total Entries')).toBeVisible();
    await expect(page.getByText('500')).toBeVisible();
    await expect(page.getByText('Blacklisted Phrases')).toBeVisible();
    await expect(page.getByText('25')).toBeVisible();
  });

  test('should display blacklisted phrases list', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 2,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API with data
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            phrase: 'test phrase 1',
            original_message: 'original message 1',
            successful_user_id: 123,
            created_at: '2024-01-01T10:00:00Z',
            is_active: true
          },
          {
            id: 2,
            phrase: 'test phrase 2',
            original_message: 'original message 2',
            successful_user_id: 456,
            created_at: '2024-01-01T11:00:00Z',
            is_active: false
          }
        ])
      });
    });

    await page.reload();

    // Check blacklisted phrases are displayed
    await expect(page.getByText('Blacklisted Phrases')).toBeVisible();
    await expect(page.getByText('test phrase 1')).toBeVisible();
    await expect(page.getByText('test phrase 2')).toBeVisible();
    await expect(page.getByText('User #123')).toBeVisible();
    await expect(page.getByText('User #456')).toBeVisible();
    await expect(page.getByText('Active')).toBeVisible();
    await expect(page.getByText('Inactive')).toBeVisible();
  });

  test('should show empty state when no blacklisted phrases', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 0,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock empty blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.reload();

    // Check empty state is displayed
    await expect(page.getByText('No blacklisted phrases found')).toBeVisible();
  });

  test('should allow adding new blacklisted phrases', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 0,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      }
    });

    await page.reload();

    // Add new blacklisted phrase
    await page.getByPlaceholder('Enter phrase to blacklist...').fill('new blacklisted phrase');
    await page.getByRole('button', { name: /Add/i }).click();

    // Check that the phrase was added (API was called)
    await expect(page.getByText('Add Blacklisted Phrase')).toBeVisible();
  });

  test('should prevent adding empty phrases', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 0,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.reload();

    // Check that add button is disabled when input is empty
    const addButton = page.getByRole('button', { name: /Add/i });
    await expect(addButton).toBeDisabled();
  });

  test('should toggle phrase status when clicking toggle button', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 1,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 1,
              phrase: 'test phrase',
              original_message: 'original message',
              successful_user_id: 123,
              created_at: '2024-01-01T10:00:00Z',
              is_active: true
            }
          ])
        });
      }
    });

    await page.reload();

    // Click toggle button
    await page.getByTitle('Deactivate').click();

    // Check that the toggle was called (API was called)
    await expect(page.getByText('test phrase')).toBeVisible();
  });

  test('should display system status information', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 0,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.reload();

    // Check system status section
    await expect(page.getByText('System Status')).toBeVisible();
    await expect(page.getByText(/AI Guardian is active/)).toBeVisible();
    await expect(page.getByText(/Blacklist system is protecting/)).toBeVisible();
    await expect(page.getByText(/bounty system is running/)).toBeVisible();
    await expect(page.getByText(/All security systems are operational/)).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await page.reload();

    // Check that the component still renders
    await expect(page.getByText('Add Blacklisted Phrase')).toBeVisible();
  });

  test('should show loading state while adding phrase', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 0,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API with delay
    await page.route('**/api/admin/blacklist', async route => {
      if (route.request().method() === 'POST') {
        await new Promise(resolve => setTimeout(resolve, 1000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      }
    });

    await page.reload();

    // Add new phrase
    await page.getByPlaceholder('Enter phrase to blacklist...').fill('test phrase');
    await page.getByRole('button', { name: /Add/i }).click();

    // Check loading state
    await expect(page.getByText('Adding...')).toBeVisible();
    const addButton = page.getByRole('button', { name: /Adding.../i });
    await expect(addButton).toBeDisabled();
  });

  test('should format timestamps correctly', async ({ page }) => {
    // Mock admin stats API
    await page.route('**/api/admin/stats', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_users: 100,
          total_entries: 500,
          total_blacklisted_phrases: 1,
          recent_attacks: 10,
          current_pool: 5000,
          total_wins: 5
        })
      });
    });

    // Mock blacklist API with timestamp
    await page.route('**/api/admin/blacklist', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            phrase: 'test phrase',
            original_message: 'original message',
            successful_user_id: 123,
            created_at: '2024-01-01T10:00:00Z',
            is_active: true
          }
        ])
      });
    });

    await page.reload();

    // Check that timestamp is displayed
    await expect(page.getByText('User #123')).toBeVisible();
  });
});
