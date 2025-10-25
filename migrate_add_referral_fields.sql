-- Migration to add referral tracking fields
-- Run this against your PostgreSQL database

ALTER TABLE free_question_usage
ADD COLUMN IF NOT EXISTS referred_by VARCHAR(255),
ADD COLUMN IF NOT EXISTS referrer_reward_pending BOOLEAN DEFAULT FALSE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_free_question_usage_referred_by ON free_question_usage(referred_by);
