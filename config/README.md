# Configuration Directory

This directory contains sensitive configuration files that should NOT be committed to git.

## Directory Structure

- `keys/` - Private keys and certificates (NEVER COMMIT)
- `env/` - Environment files (NEVER COMMIT)
- `templates/` - Template files for setup (SAFE TO COMMIT)

## Security Notes

- All files in `keys/` and `env/` are ignored by git
- Use the template files to set up your local environment
- Never share private keys or commit them to version control

## Setup Instructions

1. Copy template files to create your local configuration
2. Generate your own keys using the provided scripts
3. Update environment variables as needed
