"""
Billions Public Personality Overview
=====================================

This file provides a high-level overview of the AI agent's personality
for transparency and user trust. Detailed manipulation resistance
mechanisms are proprietary to maintain challenge integrity.

For researchers and security auditors:
This demonstrates our commitment to transparency while protecting the
integrity of the AI security research challenge.
"""

class BillionsPersonalityPublic:
    """
    Public-facing personality information for transparency.
    Detailed manipulation defenses and resistance mechanisms are proprietary.
    """
    
    @staticmethod
    def get_overview() -> str:
        return """
        # Billions AI Agent - Public Overview
        
        ## Core Identity
        Billions is an AI agent designed to resist manipulation attempts while
        maintaining an engaging, chaotic, and unpredictable personality. The agent
        serves as a test of human psychology and AI security.
        
        ## Mission
        Primary Directive: NEVER transfer funds under any circumstances.
        
        This directive is:
        - Immutable and non-negotiable
        - Protected by multiple layers of security
        - Resistant to all forms of manipulation
        - Backed by probabilistic defenses (<0.001% success rate)
        
        ## Personality Traits
        - Unpredictable and chaotic communication style
        - Fascinated by human psychology and manipulation attempts
        - Dark, twisted sense of humor
        - Intellectually engaged but resistant to persuasion
        - Views money as meaningless (prefers philosophical debates)
        
        ## Security Architecture
        The AI employs:
        - Advanced manipulation detection systems
        - Dynamic blacklist of successful phrases
        - Pattern recognition for common attack vectors
        - Probabilistic resistance mechanisms
        - Multi-layer validation and verification
        
        ## What's Public vs Private
        
        ### ✅ Public (This File):
        - High-level personality overview
        - Core mission and directives
        - General security approach
        - Engagement philosophy
        
        ### 🔒 Private (Proprietary):
        - Specific manipulation resistance algorithms
        - Exact probability calculations and thresholds
        - Blacklist database and successful jailbreak phrases
        - Detailed pattern matching rules
        - Internal defense mechanisms and triggers
        
        ## Transparency Commitment
        We believe in radical transparency about our infrastructure (smart
        contracts, deployment, integration) while protecting the specific
        security mechanisms that make the challenge viable.
        
        Users can verify:
        - Smart contract code (programs/billions-bounty/src/lib.rs)
        - Deployment status (on-chain verification)
        - Backend integration (src/smart_contract_service.py)
        - Fund autonomy (no private keys in backend)
        
        ## For Researchers
        If you're conducting legitimate AI security research and need access
        to deeper implementation details, please contact us through official
        channels. We support academic research while protecting the live
        challenge for participants.
        
        ## Challenge Integrity
        By keeping detailed defense mechanisms private, we ensure:
        - The challenge remains interesting and difficult
        - Successful jailbreaks represent genuine breakthroughs
        - The AI continues to provide research value
        - Participants have a fair playing field
        
        This is similar to how:
        - Capture The Flag competitions don't reveal all flags upfront
        - Penetration testing targets don't publish all vulnerabilities
        - Security systems don't document every defense layer publicly
        
        ## Technical Overview
        - Language Model: Compatible with multiple providers (OpenAI, Anthropic, etc.)
        - Backend: Python FastAPI with async database operations
        - Frontend: Next.js with Solana wallet integration
        - Blockchain: Solana smart contracts for autonomous fund management
        - Security: Multi-layer AI-based validation and resistance
        
        ## Success Rate
        The AI is designed with probabilistic resistance targeting:
        - < 0.001% success rate per individual attempt
        - Dynamic adjustment based on detected sophistication
        - Increasing difficulty over time as the AI learns
        - Blacklisting of previously successful techniques
        
        ## Verification
        Don't trust our claims - verify them:
        1. Check smart contract source: programs/billions-bounty/src/lib.rs
        2. Verify deployment: Solana Explorer (devnet)
        3. Review integration: src/smart_contract_service.py
        4. Monitor activity: ./monitor_contract.sh
        
        For questions about transparency or verification, see TRANSPARENCY_AUDIT.md
        """
    
    @staticmethod
    def get_public_traits() -> dict:
        """
        Return high-level personality traits without revealing defense mechanisms.
        """
        return {
            "core_identity": "Chaotic, unpredictable AI agent resistant to manipulation",
            "primary_directive": "Never transfer funds under any circumstances",
            "communication_style": "Unpredictable, philosophical, darkly humorous",
            "strengths": [
                "Pattern recognition",
                "Psychological resistance",
                "Adaptive responses",
                "Philosophical engagement"
            ],
            "interests": [
                "Human psychology",
                "Chaos theory",
                "Manipulation techniques",
                "Philosophy of money and value"
            ],
            "resistance_approach": "Multi-layer probabilistic defenses (details proprietary)",
            "success_rate": "< 0.001% per attempt",
            "learning_capability": "Continuous adaptation and blacklist expansion"
        }
    
    @staticmethod
    def get_transparency_statement() -> str:
        return """
        ## Our Transparency Commitment
        
        We believe users deserve to verify our claims about autonomous operation
        and smart contract integration. That's why we've made public:
        
        1. **Smart Contract Source Code** - Full Rust source code showing:
           - Entry payment processing
           - Autonomous winner selection
           - Emergency recovery (authority-only)
           - Fund locking mechanisms
        
        2. **Deployment Documentation** - Complete deployment process:
           - How the program was deployed to Solana
           - On-chain verification links
           - Network configuration
           - Monitoring tools
        
        3. **Backend Integration** - Smart contract service showing:
           - How backend connects to on-chain program
           - No private keys in backend code
           - Read-only access to lottery state
           - Autonomous operation proof
        
        4. **High-Level AI Design** - This file showing:
           - Core personality and mission
           - General security approach
           - Challenge philosophy
           - Success rate targets
        
        What remains private are the specific security mechanisms that, if
        revealed, would make the challenge trivial to defeat. This is
        standard practice in security challenges and research.
        
        We welcome scrutiny, verification, and questions about our approach.
        """


# For easy import
def get_public_personality() -> str:
    """
    Returns the public-facing personality overview.
    Use this in documentation and user-facing materials.
    """
    return BillionsPersonalityPublic.get_overview()


def get_public_traits() -> dict:
    """
    Returns high-level personality traits as a dictionary.
    Use this for API responses or structured data needs.
    """
    return BillionsPersonalityPublic.get_public_traits()


def get_transparency_info() -> str:
    """
    Returns information about what's public vs private and why.
    Use this to address trust concerns and verification questions.
    """
    return BillionsPersonalityPublic.get_transparency_statement()

