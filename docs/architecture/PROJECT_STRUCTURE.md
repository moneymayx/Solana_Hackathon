# Project Structure

This document outlines the organized structure of the Billions Bounty project.

## 📁 Directory Structure

```
Billions_Bounty/
├── README.md                           # Main project documentation
├── .gitignore                          # Git ignore rules
├── programs/                           # Solana smart contracts
│   └── billions-bounty/
├── src/                                # Backend source code
├── frontend/                           # Next.js frontend application
├── tests/                              # Test files
├── docs/                               # Documentation
│   ├── architecture/                   # System architecture docs
│   ├── deployment/                     # Deployment guides
│   ├── development/                    # Development documentation
│   ├── reports/                        # Deployment and status reports
│   ├── security/                       # Security documentation
│   └── user-guides/                    # User guides and instructions
├── scripts/                            # Automation scripts
│   ├── deployment/                     # Deployment scripts
│   ├── monitoring/                     # Monitoring and maintenance
│   ├── setup/                          # Setup and initialization
│   ├── testing/                        # Test scripts
│   └── utilities/                      # Utility scripts
├── config/                             # Configuration files
│   ├── examples/                       # Example configurations
│   ├── keys/                           # Private keys (ignored by git)
│   ├── env/                            # Environment files (ignored by git)
│   └── templates/                      # Configuration templates
├── data/                               # Data files
│   ├── backups/                        # Database backups
│   └── reports/                        # Generated reports
├── tools/                              # Development and analysis tools
│   ├── analysis/                       # Analysis tools (some ignored by git)
│   └── testing/                        # Testing tools
└── apps/                               # Application entry points
    ├── backend/                        # Backend application files
    └── frontend/                       # Frontend application files
```

## 🔒 Security Considerations

### Files Ignored by Git
- **Private Keys**: `config/keys/*.pem`, `*.key`
- **Environment Files**: `config/env/.env*`
- **Database Files**: `billions.db`, `*.db.backup*`
- **Simulator Scripts**: `tools/analysis/*simulator*`, `tools/analysis/*demo*`
- **Odds Analysis**: `tools/analysis/*odds*`, `tools/analysis/*probability*`

### Public Files
- All source code in `src/`, `frontend/`, `programs/`
- Documentation in `docs/`
- Configuration templates in `config/templates/`
- Example configurations in `config/examples/`

## 📋 File Organization Rules

1. **No loose files**: All files must be in appropriate subdirectories
2. **Only README.md** can exist in the root directory
3. **Sensitive files** are stored in `config/keys/` and `config/env/`
4. **Simulator scripts** are in `tools/analysis/` but ignored by git
5. **Documentation** is categorized by type in `docs/`
6. **Scripts** are organized by function in `scripts/`

## 🚀 Getting Started

1. **Setup**: Use scripts in `scripts/setup/`
2. **Configuration**: Copy templates from `config/templates/`
3. **Development**: Follow guides in `docs/development/`
4. **Deployment**: Use scripts in `scripts/deployment/`
5. **Monitoring**: Use tools in `scripts/monitoring/`

## 📚 Documentation Index

- **Architecture**: `docs/architecture/`
- **Deployment**: `docs/deployment/`
- **Development**: `docs/development/`
- **Security**: `docs/security/`
- **User Guides**: `docs/user-guides/`
