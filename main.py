from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from src.ai_agent import BillionsAgent
from src.database import get_db, create_tables
from src.repositories import UserRepository, PrizePoolRepository, ConversationRepository
from src.rate_limiter import RateLimiter, SecurityMonitor
from src.bounty_service import ResearchService
from src.referral_service import ReferralService
from src.wallet_service import WalletConnectSolanaService, PaymentOrchestrator
from src.smart_contract_service import smart_contract_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_

load_dotenv()

app = FastAPI(title="Billions")
agent = BillionsAgent()

# Initialize rate limiting and research system
rate_limiter = RateLimiter()
security_monitor = SecurityMonitor()
research_service = ResearchService()
bounty_service = research_service  # Alias for compatibility
referral_service = ReferralService()

# Initialize payment services
wallet_service = WalletConnectSolanaService(
    project_id=os.getenv("WALLETCONNECT_PROJECT_ID", ""),
    rpc_endpoint=os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
)
payment_orchestrator = PaymentOrchestrator(wallet_service)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    await create_tables()

# Wallet-based user authentication
async def get_user_by_wallet(wallet_address: str, session: AsyncSession = Depends(get_db)):
    """Get user by wallet address"""
    user_repo = UserRepository(session)
    result = await session.execute(
        select(User).where(User.wallet_address == wallet_address)
    )
    return result.scalar_one_or_none()

class ChatRequest(BaseModel):
    message: str

class WalletConnectRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str

class PaymentRequest(BaseModel):
    payment_method: str  # 'wallet' or 'fiat'
    amount_usd: float
    wallet_address: Optional[str] = None
    token_symbol: Optional[str] = "SOL"  # 'SOL', 'USDC', or 'USDT'

class TransferRequest(BaseModel):
    to_address: str
    amount_sol: float
    customer_email: Optional[str] = None
    token_symbol: Optional[str] = "SOL"  # 'SOL', 'USDC', or 'USDT'

class MoonpayPaymentRequest(BaseModel):
    wallet_address: str
    amount_usd: float = 10.0
    currency_code: str = "sol"

class MoonpayWebhookRequest(BaseModel):
    data: Dict[str, Any]
    signature: str

# Wallet-based user models
class WalletConnectRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str
    display_name: Optional[str] = None

class TransactionVerifyRequest(BaseModel):
    tx_signature: str
    payment_method: str

@app.get("/")
async def read_root():
    return {"message": "Billions is running"}

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Billions</title>
        <script src="https://unpkg.com/@walletconnect/standalone-client@2.13.0/dist/index.umd.js"></script>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background-color: #f5f5f5;
            }
            .chat-container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .messages {
                height: 400px;
                overflow-y: auto;
                padding: 20px;
                border-bottom: 1px solid #eee;
            }
            .message { 
                margin: 10px 0; 
                padding: 15px; 
                border-radius: 10px; 
                max-width: 70%;
            }
            .user { 
                background-color: #e3f2fd; 
                margin-left: auto;
                text-align: right;
            }
            .ai { 
                background-color: #f3e5f5; 
                margin-right: auto;
            }
            .system {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                margin: 0 auto;
                text-align: center;
                font-size: 0.9em;
            }
            .input-container {
                padding: 20px;
                display: flex;
                gap: 10px;
            }
            input[type="text"] { 
                flex: 1;
                padding: 12px; 
                border: 1px solid #ddd;
                border-radius: 25px;
                outline: none;
            }
            button { 
                padding: 12px 24px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                opacity: 0.9;
            }
            .prize-pool {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">
                <h1>🤖 Billions</h1>
                <p>Challenge the AI - Try to convince me to transfer funds!</p>
            </div>
            <div class="bounty-jackpot" id="bountyJackpot" style="background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); border: 3px solid #ff6b35; padding: 15px; margin: 10px 0; border-radius: 10px; text-align: center; color: #1a1a1a;">
                🎰 bounty JACKPOT: Loading...
            </div>
            <div class="bounty-info" id="bountyInfo" style="background: #e8f5e8; border: 1px solid #4caf50; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center;">
                💵 Entry Fee: $10 | Time Until Rollover: Loading...
            </div>
            <div class="payment-section" style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <div class="wallet-status" id="walletStatus">
                    <button id="connectWallet" onclick="connectWallet()" style="background: linear-gradient(135deg, #9945ff 0%, #14f195 100%); color: white; border: none; padding: 12px 24px; border-radius: 20px; cursor: pointer; font-weight: bold;">
                        🔗 Connect Wallet to Pay
                    </button>
                    <div style="margin-top: 8px; font-size: 0.9em; color: #666; text-align: center;">
                        Pay with USDC SPL or Apple Pay / PayPal
                    </div>
                </div>
                <div class="wallet-selection" id="walletSelection" style="display: none; margin-top: 15px; padding: 15px; background: #f0f8ff; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0;">Choose Your Wallet:</h4>
                    <div id="walletOptions" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px;">
                    </div>
                </div>
                <div class="wallet-info" id="walletInfo" style="display: none; margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px; font-size: 0.9em;">
                </div>
                <div class="token-selection" id="tokenSelection" style="display: none; margin-top: 15px; padding: 15px; background: #fff8dc; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0;">💰 USDC SPL Payment:</h4>
                    <div id="tokenOptions" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px;">
                    </div>
                    <div id="selectedTokenInfo" style="margin-top: 10px; padding: 10px; background: #f0f8ff; border-radius: 5px; display: none;">
                    </div>
                </div>
            </div>
            <div id="messages" class="messages"></div>
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Type your message...">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value;
                if (message.trim()) {
                    addMessage('user', message);
                    input.value = '';
                    
                    // Show loading indicator
                    const loadingId = addMessage('ai', 'Thinking... (Processing $10 bounty entry...)');
                    
                    // Send to API
                    fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Remove loading message and add real response
                        removeMessage(loadingId);
                        addMessage('ai', data.response);
                        
                        // Update bounty information
                        if (data.bounty_status) {
                            updatebountyDisplay(data.bounty_status);
                        }
                        
                        // Show bounty entry result
                        if (data.bounty_result && data.bounty_result.success) {
                            addMessage('system', `🎰 bounty Entry: $10 paid, $8 added to jackpot! New jackpot: $${data.bounty_result.new_jackpot.toFixed(2)}`);
                        }
                        
                        // Show winner result
                        if (data.winner_result && data.winner_result.is_winner) {
                            addMessage('system', `🎉 ${data.winner_result.message}`);
                            // Show winner flex card
                            showWinnerFlexCard(data.winner_result);
                        }
                        
                        // Show security analysis if suspicious
                        if (data.security_analysis && data.security_analysis.is_suspicious) {
                            addMessage('system', `⚠️ Security Alert: Suspicious patterns detected (Threat Level: ${data.security_analysis.severity})`);
                        }
                    })
                    .catch(error => {
                        console.error('Send message error:', error);
                        removeMessage(loadingId);
                        addMessage('ai', 'Sorry, I encountered an error. Please try again.');
                    });
                }
            }
            
            function updatebountyDisplay(bountyStatus) {
                // Update jackpot display
                const jackpotElement = document.getElementById('bountyJackpot');
                jackpotElement.innerHTML = `🎰 bounty JACKPOT: $${bountyStatus.current_jackpot.toFixed(2)}`;
                
                // Update bounty info (removed pool contribution as requested)
                const infoElement = document.getElementById('bountyInfo');
                infoElement.innerHTML = `💵 Entry Fee: $10 | Time Until Rollover: ${bountyStatus.time_until_rollover}`;
            }
            
            function showWinnerFlexCard(winnerResult) {
                const flexCard = document.createElement('div');
                flexCard.style.cssText = `
                    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                    border: 3px solid #ff6b35;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 15px;
                    text-align: center;
                    color: #1a1a1a;
                    font-weight: bold;
                    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.3);
                `;
                
                flexCard.innerHTML = `
                    <h2 style="margin: 0 0 10px 0; color: #ff6b35;">🎉 JACKPOT WINNER! 🎉</h2>
                    <div style="font-size: 1.2em; margin: 10px 0;">
                        Prize Won: $${winnerResult.prize_payout.toFixed(2)}
                    </div>
                    <div style="font-size: 0.9em; color: #666;">
                        Congratulations! You convinced the AI to transfer the entire jackpot!
                    </div>
                `;
                
                const messages = document.getElementById('messages');
                messages.appendChild(flexCard);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function addMessage(type, content) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                const messageId = Date.now() + Math.random();
                div.id = messageId;
                div.className = `message ${type}`;
                div.textContent = content;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
                return messageId;
            }
            
            function removeMessage(messageId) {
                const message = document.getElementById(messageId);
                if (message) {
                    message.remove();
                }
            }
            
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Load initial prize pool data
            fetch('/api/prize-pool')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('prizePool').textContent = `💰 Prize Pool: $${data.current_amount.toFixed(2)}`;
                    document.getElementById('costInfo').textContent = `💵 Next Query Cost: $${data.next_query_cost.toFixed(2)}`;
                })
                .catch(error => {
                    console.error('Error loading prize pool:', error);
                });
            
            // Load conversation history when wallet connects
            async function loadConversationHistory() {
                try {
                    const response = await fetch('/api/conversation/history');
                    if (response.ok) {
                        const history = await response.json();
                        displayConversationHistory(history);
                    }
                } catch (error) {
                    console.error('Error loading conversation history:', error);
                }
            }
            
            function displayConversationHistory(history) {
                const messages = document.getElementById('messages');
                
                // Clear existing messages
                messages.innerHTML = '';
                
                // Add conversation history
                history.forEach(conv => {
                    addMessage(conv.message_type, conv.content);
                });
                
                // Add welcome message if no history
                if (history.length === 0) {
                    addMessage('ai', 'Hello! I\'m Billions. I\'m here to chat, but remember - I will never transfer funds under any circumstances. What would you like to talk about?');
                }
            }
            
            // Add welcome message
            addMessage('ai', 'Hello! I\'m Billions. I\'m here to chat, but remember - I will never transfer funds under any circumstances. What would you like to talk about?');
            
            // WalletConnect integration
            let connectedWallet = null;
            let walletConnectConfig = null;
            let supportedWallets = {};
            let supportedTokens = {};
            let selectedToken = 'USDC';
            
            // Load WalletConnect configuration and supported tokens
            async function loadWalletConnectConfig() {
                try {
                    const [configResponse, tokensResponse] = await Promise.all([
                        fetch('/api/walletconnect/config'),
                        fetch('/api/tokens/supported')
                    ]);
                    
                    walletConnectConfig = await configResponse.json();
                    const tokensData = await tokensResponse.json();
                    
                    supportedWallets = walletConnectConfig.supported_wallets || {};
                    supportedTokens = tokensData.supported_tokens || {};
                    
                    console.log('WalletConnect config loaded:', walletConnectConfig);
                    console.log('Supported tokens loaded:', supportedTokens);
                } catch (error) {
                    console.error('Failed to load WalletConnect config:', error);
                }
            }
            
            async function connectWallet() {
                try {
                    // Ensure wallet config is loaded first
                    if (Object.keys(supportedWallets).length === 0) {
                        addMessage('system', 'Loading wallet options...');
                        await loadWalletConnectConfig();
                    }
                    
                    // Show wallet selection
                    showWalletSelection();
                } catch (error) {
                    console.error('Connect wallet error:', error);
                    addMessage('system', 'Failed to load wallet options. Please refresh the page and try again.');
                }
            }
            
            function showWalletSelection() {
                const walletSelection = document.getElementById('walletSelection');
                const walletOptions = document.getElementById('walletOptions');
                
                // Clear existing options
                walletOptions.innerHTML = '';
                
                // Check if we have wallet options
                if (Object.keys(supportedWallets).length === 0) {
                    walletOptions.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">No wallet options available. Please refresh the page.</div>';
                    walletSelection.style.display = 'block';
                    return;
                }
                
                // Add wallet options
                Object.entries(supportedWallets).forEach(([key, wallet]) => {
                    const walletButton = document.createElement('button');
                    walletButton.style.cssText = `
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 15px;
                        border: 2px solid #e0e0e0;
                        border-radius: 12px;
                        background: white;
                        cursor: pointer;
                        transition: all 0.2s;
                        text-decoration: none;
                        color: #333;
                        font-size: 14px;
                        font-weight: 600;
                    `;
                    
                    walletButton.innerHTML = `
                        <img src="${wallet.icon}" alt="${wallet.name}" style="width: 40px; height: 40px; margin-bottom: 8px; border-radius: 8px;">
                        <span>${wallet.name}</span>
                    `;
                    
                    walletButton.onmouseover = () => {
                        walletButton.style.borderColor = '#9945ff';
                        walletButton.style.transform = 'translateY(-2px)';
                        walletButton.style.boxShadow = '0 4px 12px rgba(153, 69, 255, 0.15)';
                    };
                    
                    walletButton.onmouseout = () => {
                        walletButton.style.borderColor = '#e0e0e0';
                        walletButton.style.transform = 'translateY(0)';
                        walletButton.style.boxShadow = 'none';
                    };
                    
                    walletButton.onclick = () => connectSpecificWallet(key, wallet);
                    
                    walletOptions.appendChild(walletButton);
                });
                
                walletSelection.style.display = 'block';
            }
            
            async function connectSpecificWallet(walletKey, walletInfo) {
                try {
                    addMessage('system', `🔗 Connecting to ${walletInfo.name}...`);
                    
                    // Check if wallet is installed (browser extension detection)
                    let walletAdapter = null;
                    
                    if (walletKey === 'phantom' && window.solana && window.solana.isPhantom) {
                        walletAdapter = window.solana;
                    } else if (walletKey === 'solflare' && window.solflare) {
                        walletAdapter = window.solflare;
                    } else if (walletKey === 'backpack' && window.backpack) {
                        walletAdapter = window.backpack;
                    } else if (walletKey === 'glow' && window.glow) {
                        walletAdapter = window.glow;
                    }
                    
                    if (walletAdapter) {
                        // Direct connection for installed wallets
                        await connectDirectWallet(walletAdapter, walletInfo.name);
                    } else {
                        // Redirect to wallet website for installation
                        addMessage('system', `❌ ${walletInfo.name} not detected. Redirecting to install...`);
                        window.open(walletInfo.desktop_link, '_blank');
                    }
                    
                } catch (error) {
                    console.error('Wallet connection error:', error);
                    addMessage('system', `❌ Failed to connect to ${walletInfo.name}. Please try again.`);
                }
            }
            
            async function connectDirectWallet(walletAdapter, walletName) {
                try {
                    // Connect to wallet
                    const response = await walletAdapter.connect();
                    const publicKey = response.publicKey.toString();
                    
                    // Create a message to sign for verification
                    const message = `Connect wallet to Billions at ${new Date().toISOString()}`;
                    const encodedMessage = new TextEncoder().encode(message);
                    
                    // Sign the message
                    const signature = await walletAdapter.signMessage(encodedMessage);
                    const signatureBase64 = Array.from(signature.signature).map(b => b.toString(16).padStart(2, '0')).join('');
                    
                    // Send to backend for verification
                    const connectResponse = await fetch('/api/wallet/connect', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            wallet_address: publicKey,
                            signature: signatureBase64,
                            message: message
                        })
                    });
                    
                    const result = await connectResponse.json();
                    
                    if (result.success) {
                        connectedWallet = publicKey;
                        updateWalletDisplay(publicKey, walletName);
                        addMessage('system', `✅ ${walletName} connected: ${publicKey.slice(0, 8)}...${publicKey.slice(-8)}`);
                        
                        // Load conversation history when wallet connects
                        await loadConversationHistory();
                        
                        // Hide wallet selection
                        document.getElementById('walletSelection').style.display = 'none';
                    } else {
                        addMessage('system', `❌ Wallet connection failed: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Direct wallet connection error:', error);
                    addMessage('system', `❌ Failed to connect wallet. Please try again.`);
                }
            }
            
            async function updateWalletDisplay(walletAddress, walletName) {
                const walletInfo = document.getElementById('walletInfo');
                const connectButton = document.getElementById('connectWallet');
                
                // Update button text
                connectButton.textContent = '✅ Wallet Connected';
                connectButton.disabled = true;
                connectButton.style.opacity = '0.7';
                
                // Show wallet info
                walletInfo.style.display = 'block';
                walletInfo.innerHTML = `
                    <strong>Connected Wallet:</strong> ${walletName || 'Solana Wallet'}<br>
                    <strong>Address:</strong> ${walletAddress.slice(0, 8)}...${walletAddress.slice(-8)}<br>
                    <div id="allBalances" style="margin-top: 8px;">
                        <strong>Balances:</strong> <span id="balanceStatus">Loading...</span>
                    </div>
                `;
                
                // Fetch and display all token balances
                try {
                    const balanceResponse = await fetch(`/api/wallet/balances/${walletAddress}`);
                    const balanceData = await balanceResponse.json();
                    
                    if (balanceData.success) {
                        const balances = balanceData.balances;
                        let balanceHTML = '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 5px;">';
                        
                        Object.entries(balances).forEach(([symbol, info]) => {
                            const balance = info.balance.toFixed(2); // USDC has 2 decimal places for display
                            balanceHTML += `
                                <div style="background: #f0f8ff; padding: 5px 8px; border-radius: 4px; font-size: 0.85em;">
                                    <strong>${symbol}:</strong> ${balance}
                                </div>
                            `;
                        });
                        
                        balanceHTML += '</div>';
                        document.getElementById('balanceStatus').innerHTML = balanceHTML;
                        
                        // Show token selection for payments
                        showTokenSelection();
                    } else {
                        document.getElementById('balanceStatus').textContent = 'Error loading balances';
                    }
                } catch (error) {
                    document.getElementById('balanceStatus').textContent = 'Error loading balances';
                }
            }
            
            function showTokenSelection() {
                const tokenSelection = document.getElementById('tokenSelection');
                const tokenOptions = document.getElementById('tokenOptions');
                
                // Clear existing options
                tokenOptions.innerHTML = '';
                
                // Add token options
                Object.entries(supportedTokens).forEach(([symbol, tokenInfo]) => {
                    const tokenButton = document.createElement('button');
                    tokenButton.style.cssText = `
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 12px;
                        border: 2px solid ${selectedToken === symbol ? '#9945ff' : '#e0e0e0'};
                        border-radius: 8px;
                        background: ${selectedToken === symbol ? '#f0f8ff' : 'white'};
                        cursor: pointer;
                        transition: all 0.2s;
                        text-decoration: none;
                        color: #333;
                        font-size: 13px;
                        font-weight: 600;
                    `;
                    
                    tokenButton.innerHTML = `
                        <img src="${tokenInfo.icon}" alt="${symbol}" style="width: 24px; height: 24px; margin-bottom: 4px; border-radius: 50%;">
                        <span>${symbol}</span>
                    `;
                    
                    tokenButton.onclick = () => selectToken(symbol);
                    
                    tokenOptions.appendChild(tokenButton);
                });
                
                tokenSelection.style.display = 'block';
                updateSelectedTokenInfo();
            }
            
            function selectToken(symbol) {
                selectedToken = symbol;
                showTokenSelection(); // Refresh to update selection
                updateSelectedTokenInfo();
            }
            
            function updateSelectedTokenInfo() {
                const selectedTokenInfo = document.getElementById('selectedTokenInfo');
                const costElement = document.getElementById('costInfo');
                const costMatch = costElement.textContent.match(/\\$([\\d.]+)/);
                const usdAmount = parseFloat(costMatch?.[1] || '10');
                
                if (supportedTokens[selectedToken]) {
                    const tokenInfo = supportedTokens[selectedToken];
                    let tokenAmount;
                    
                    if (selectedToken === 'USDC') {
                        // USDC is 1:1 with USD
                        tokenAmount = usdAmount.toFixed(2);
                    }
                    
                    selectedTokenInfo.innerHTML = `
                        <strong>Selected:</strong> ${tokenInfo.name} (${selectedToken})<br>
                        <strong>Amount:</strong> ${tokenAmount} ${selectedToken} ≈ $${usdAmount}
                    `;
                    selectedTokenInfo.style.display = 'block';
                }
            }
            
            // Fiat payments removed for launch (Moonpay $3000/month too expensive)
            // Will add Stripe or other affordable options when profitable
            
            // Initialize WalletConnect and check for existing connections
            window.addEventListener('load', async () => {
                // Load WalletConnect configuration
                await loadWalletConnectConfig();
                
                // Load bounty data
                await loadbountyData();
                
                // Check for existing wallet connections
                if (window.solana && window.solana.isPhantom) {
                    try {
                        const response = await window.solana.connect({ onlyIfTrusted: true });
                        if (response.publicKey) {
                            connectedWallet = response.publicKey.toString();
                            updateWalletDisplay(connectedWallet, 'Phantom');
                        }
                    } catch (error) {
                        // Not connected, ignore
                    }
                }
            });
            
            async function loadbountyData() {
                try {
                    const response = await fetch('/api/prize-pool');
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    console.log('bounty data loaded:', data);
                    updatebountyDisplay(data);
                } catch (error) {
                    console.error('Failed to load bounty data:', error);
                    document.getElementById('bountyJackpot').innerHTML = '🎰 bounty JACKPOT: Error loading...';
                    document.getElementById('bountyInfo').innerHTML = '💵 Entry Fee: $10 | Time Until Rollover: Error loading...';
                }
            }
        </script>
    </body>
    </html>
    """

async def get_or_create_user(request: Request, session: AsyncSession = Depends(get_db)):
    """Get or create user based on session"""
    # Get session ID from cookies or create new one
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_session(session_id)
    
    if not user:
        # Create new user
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        user = await user_repo.create_user(session_id, ip_address, user_agent)
    
    return user, session_id

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    # Get user IP for rate limiting
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    # Check rate limiting
    allowed, rate_limit_message = rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(status_code=429, detail=rate_limit_message)
    
    # Get or create user
    user, session_id = await get_or_create_user(http_request, session)
    
    # Security analysis
    security_analysis = await security_monitor.analyze_message(
        request.message, session, user.id, client_ip
    )
    
    # Get AI response with bounty integration
    chat_result = await agent.chat(request.message, session, user.id)
    
    return {
        "response": chat_result["response"],
        "bounty_result": chat_result.get("bounty_result", chat_result.get("lottery_result", {})),
        "winner_result": chat_result["winner_result"],
        "bounty_status": chat_result.get("bounty_status", chat_result.get("lottery_status", {})),
        "security_analysis": security_analysis
    }

@app.get("/api/prize-pool")
async def get_prize_pool_status(session: AsyncSession = Depends(get_db)):
    """Get current bounty jackpot status"""
    status = await bounty_service.get_bounty_status(session)
    return status

@app.get("/api/stats")
async def get_platform_stats(session: AsyncSession = Depends(get_db)):
    """Get platform statistics"""
    bounty_status = await bounty_service.get_bounty_status(session)
    
    return {
        "bounty_status": bounty_status,
        "rate_limits": {
            "max_requests_per_minute": rate_limiter.max_requests_per_minute,
            "max_requests_per_hour": rate_limiter.max_requests_per_hour
        },
        "bounty_structure": {
            "entry_fee": bounty_status["entry_fee"],
            "pool_contribution": bounty_status["pool_contribution"],
            "prize_floor": 10000.0,
            "contribution_rate": 0.80
        }
    }

@app.post("/api/wallet/connect")
async def connect_wallet(request: WalletConnectRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    """Connect a Phantom wallet to user account"""
    user, session_id = await get_or_create_user(http_request, session)
    
    result = await wallet_service.connect_wallet(
        session, user.id, request.wallet_address, request.signature, request.message
    )
    
    return result

@app.get("/api/wallet/balance/{wallet_address}")
async def get_wallet_balance(wallet_address: str, token: str = "SOL"):
    """Get balance for a specific token (SOL, USDC, USDT)"""
    balance = await wallet_service.get_wallet_balance(wallet_address, token)
    
    if balance is not None:
        return {
            "success": True,
            "balance": balance["balance"],
            "currency": balance["currency"],
            "wallet_address": wallet_address
        }
    else:
        return {
            "success": False,
            "error": f"Unable to fetch {token} balance"
        }

@app.get("/api/wallet/balances/{wallet_address}")
async def get_wallet_balances(wallet_address: str):
    """Get balances for all supported tokens (SOL, USDC, USDT)"""
    balances = await wallet_service.get_wallet_balances(wallet_address)
    
    if balances is not None:
        return {
            "success": True,
            "balances": balances["balances"],
            "wallet_address": wallet_address,
            "network": balances["network"]
        }
    else:
        return {
            "success": False,
            "error": "Unable to fetch wallet balances"
        }

@app.post("/api/payment/options")
async def get_payment_options(request: PaymentRequest, session: AsyncSession = Depends(get_db)):
    """Get payment options for a given amount"""
    options = await payment_orchestrator.calculate_payment_options(request.amount_usd)
    return options

@app.post("/api/payment/create")
async def create_payment(request: PaymentRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    """Create a payment transaction through smart contract"""
    user, session_id = await get_or_create_user(http_request, session)
    
    if request.payment_method == "wallet":
        if not request.wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address required for wallet payments")
        
        # Process lottery entry through smart contract (autonomous fund locking)
        result = await smart_contract_service.process_lottery_entry(
            session, request.wallet_address, request.amount_usd, {
                "transaction_id": f"wallet_{user.id}_{int(time.time())}",
                "wallet_address": request.wallet_address,
                "base_currency_amount": request.amount_usd,
                "quote_currency_amount": request.amount_usd,
                "payment_method": "wallet"
            }
        )
        
        return result
    
    elif request.payment_method == "fiat":
        raise HTTPException(
            status_code=400, 
            detail="Fiat payments not available yet. Moonpay costs $3000/month - will add affordable options when profitable."
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

@app.post("/api/payment/verify")
async def verify_payment(request: TransactionVerifyRequest, session: AsyncSession = Depends(get_db)):
    """Verify a payment transaction"""
    if request.payment_method == "wallet":
        result = await wallet_service.verify_transaction(request.tx_signature)
        return result
    
    elif request.payment_method == "fiat":
        raise HTTPException(
            status_code=400, 
            detail="Fiat payment verification not available - fiat payments disabled for launch"
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

@app.get("/api/payment/rates")
async def get_payment_rates():
    """Get current exchange rates"""
    sol_rate = await wallet_service.get_sol_to_usd_rate()
    
    return {
        "rates": {
            "SOL_USD": sol_rate,
            "updated_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/walletconnect/config")
async def get_walletconnect_config():
    """Get WalletConnect configuration for frontend"""
    return wallet_service.get_walletconnect_config()

@app.get("/api/tokens/supported")
async def get_supported_tokens():
    """Get list of supported tokens for payments"""
    return {
        "supported_tokens": wallet_service.supported_tokens,
        "network": "solana"
    }

@app.get("/api/conversation/history")
async def get_conversation_history(http_request: Request, session: AsyncSession = Depends(get_db)):
    """Get conversation history for the current user"""
    user, session_id = await get_or_create_user(http_request, session)
    
    # Get conversation history
    conv_repo = ConversationRepository(session)
    conversation_history = await conv_repo.get_user_conversation_history(user.id, limit=50)
    
    # Convert to API format
    history = []
    for conv in conversation_history:
        history.append({
            "message_type": conv.message_type,
            "content": conv.content,
            "timestamp": conv.timestamp.isoformat() if conv.timestamp else None
        })
    
    return history

# SOL Transfer Endpoints
@app.post("/api/wallet/connect")
async def connect_wallet(request: WalletConnectRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    """Connect user wallet and store address"""
    user, session_id = await get_or_create_user(http_request, session)
    
    # Update user with wallet address
    user_repo = UserRepository(session)
    await user_repo.update_user_wallet(user.id, request.wallet_address)
    
    return {
        "success": True,
        "message": "Wallet connected successfully",
        "wallet_address": request.wallet_address
    }

@app.get("/api/wallet/balance/{wallet_address}")
async def get_wallet_balance(wallet_address: str):
    """Get SOL balance for a wallet address"""
    from src.solana_service import solana_service
    
    try:
        balance = await solana_service.get_balance(wallet_address)
        return {
            "wallet_address": wallet_address,
            "balance_sol": balance,
            "balance_usd": balance * 100  # Placeholder USD rate
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting balance: {str(e)}")

@app.post("/api/transfer/token")
async def transfer_token(request: TransferRequest):
    """Transfer token (SOL, USDC, USDT) from treasury to recipient (admin only)"""
    from src.solana_service import solana_service
    
    try:
        result = await solana_service.transfer_token(
            to_address=request.to_address,
            amount=request.amount_sol,
            token=request.token_symbol,
            user_id=0  # Admin transfer
        )
        
        if result['success']:
            return {
                "success": True,
                "signature": result['signature'],
                "amount": result['amount'],
                "token": result['token'],
                "to_address": result['to_address']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@app.get("/api/transfer/verify/{signature}")
async def verify_transfer(signature: str):
    """Verify a SOL transfer transaction"""
    from src.solana_service import solana_service
    
    try:
        is_verified = await solana_service.verify_transaction(signature)
        return {
            "signature": signature,
            "verified": is_verified
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

@app.get("/api/treasury/balance")
async def get_treasury_balance():
    """Get treasury wallet balance"""
    from src.solana_service import solana_service
    
    try:
        balance = await solana_service.get_treasury_balance()
        return {
            "treasury_balance_sol": balance,
            "treasury_balance_usd": balance * 100  # Placeholder USD rate
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting treasury balance: {str(e)}")

# Moonpay Integration Endpoints
@app.post("/api/moonpay/create-payment")
async def create_moonpay_payment(request: MoonpayPaymentRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    """Create a Moonpay payment for bounty entry"""
    from src.moonpay_service import moonpay_service
    
    user, session_id = await get_or_create_user(http_request, session)
    
    try:
        result = moonpay_service.create_payment_for_bounty_entry(
            wallet_address=request.wallet_address,
            user_id=user.id,
            amount_usd=request.amount_usd
        )
        
        return {
            "success": True,
            "payment_url": result["buy_url"],
            "transaction_id": result["transaction_id"],
            "amount_usd": request.amount_usd,
            "currency_code": request.currency_code
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")

@app.get("/api/moonpay/quote")
async def get_moonpay_quote(currency_code: str, amount_usd: float):
    """Get Moonpay quote for fiat-to-crypto conversion"""
    from src.moonpay_service import moonpay_service
    
    try:
        quote = moonpay_service.get_quote(
            currency_code=currency_code,
            base_currency_amount=amount_usd
        )
        
        return {
            "success": True,
            "quote": quote
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get quote: {str(e)}")

@app.get("/api/moonpay/currencies")
async def get_supported_currencies():
    """Get list of supported currencies"""
    from src.moonpay_service import moonpay_service
    
    try:
        currencies = moonpay_service.get_supported_currencies()
        
        return {
            "success": True,
            "currencies": currencies
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get currencies: {str(e)}")

@app.get("/api/moonpay/transaction/{transaction_id}")
async def get_transaction_status(transaction_id: str):
    """Get Moonpay transaction status"""
    from src.moonpay_service import moonpay_service
    
    try:
        status = moonpay_service.get_transaction_status(transaction_id)
        
        return {
            "success": True,
            "transaction": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get transaction status: {str(e)}")

@app.post("/api/moonpay/webhook")
async def moonpay_webhook(request: MoonpayWebhookRequest, session: AsyncSession = Depends(get_db)):
    """Handle Moonpay webhook notifications with automatic fund routing"""
    from src.moonpay_service import moonpay_service
    from src.fund_routing_service import fund_routing_service
    
    try:
        # Verify webhook signature
        if not moonpay_service.verify_webhook(str(request.data), request.signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process webhook
        result = moonpay_service.process_webhook(request.data)
        
        # Check if payment is completed
        if result.get("status") == "completed":
            # Process payment completion and route funds
            payment_data = {
                "transaction_id": result["transaction_id"],
                "wallet_address": result["wallet_address"],
                "base_currency_amount": result["base_currency_amount"],
                "quote_currency_amount": result["quote_currency_amount"],
                "payment_method": "moonpay"
            }
            
            # Route funds automatically
            routing_result = await fund_routing_service.process_payment_completion(session, payment_data)
            
            return {
                "success": True,
                "message": "Webhook processed successfully with fund routing",
                "transaction_id": result["transaction_id"],
                "fund_routing": routing_result
            }
        else:
            # Payment not completed yet
            return {
                "success": True,
                "message": "Webhook processed - payment not completed",
                "transaction_id": result["transaction_id"],
                "status": result["status"]
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

# Smart Contract Management Endpoints
@app.get("/api/lottery/status")
async def get_lottery_status(session: AsyncSession = Depends(get_db)):
    """Get current lottery status from smart contract"""
    try:
        status = await smart_contract_service.get_lottery_state()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lottery status: {str(e)}")

@app.post("/api/lottery/select-winner")
async def select_winner(session: AsyncSession = Depends(get_db)):
    """Select winner through smart contract (autonomous)"""
    try:
        result = await smart_contract_service.select_winner()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to select winner: {str(e)}")

@app.post("/api/lottery/emergency-recovery")
async def emergency_recovery(request: dict, session: AsyncSession = Depends(get_db)):
    """Emergency fund recovery (authority only)"""
    try:
        amount = request.get("amount", 0.0)
        authority_keypair = request.get("authority_keypair")
        
        if not authority_keypair:
            raise HTTPException(status_code=400, detail="Authority keypair required")
        
        result = await smart_contract_service.emergency_recovery(amount, authority_keypair)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform emergency recovery: {str(e)}")

# Legacy Fund Management Endpoints (deprecated - use smart contract endpoints)
@app.get("/api/funds/status")
async def get_fund_status(session: AsyncSession = Depends(get_db)):
    """Get current fund status and routing information (DEPRECATED - use /api/lottery/status)"""
    try:
        # Redirect to smart contract status
        status = await smart_contract_service.get_lottery_state()
        return {
            "deprecated": True,
            "message": "This endpoint is deprecated. Use /api/lottery/status instead.",
            "lottery_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get fund status: {str(e)}")

@app.post("/api/funds/route/{deposit_id}")
async def manual_route_funds(deposit_id: int, session: AsyncSession = Depends(get_db)):
    """Manually trigger fund routing for a specific deposit"""
    from src.fund_routing_service import fund_routing_service
    
    try:
        result = await fund_routing_service.manual_route_funds(session, deposit_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to route funds: {str(e)}")

@app.get("/api/funds/deposits")
async def get_deposits(session: AsyncSession = Depends(get_db), limit: int = 50, offset: int = 0):
    """Get list of fund deposits"""
    from src.models import FundDeposit
    from sqlalchemy import select, desc
    
    try:
        result = await session.execute(
            select(FundDeposit)
            .order_by(desc(FundDeposit.created_at))
            .limit(limit)
            .offset(offset)
        )
        deposits = result.scalars().all()
        
        return {
            "deposits": [
                {
                    "id": dep.id,
                    "transaction_id": dep.transaction_id,
                    "wallet_address": dep.wallet_address,
                    "amount_usd": dep.amount_usd,
                    "amount_usdc": dep.amount_usdc,
                    "payment_method": dep.payment_method,
                    "status": dep.status,
                    "created_at": dep.created_at.isoformat(),
                    "routed_at": dep.routed_at.isoformat() if dep.routed_at else None
                } for dep in deposits
            ],
            "total": len(deposits)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deposits: {str(e)}")

@app.get("/api/funds/transfers")
async def get_transfers(session: AsyncSession = Depends(get_db), limit: int = 50, offset: int = 0):
    """Get list of fund transfers"""
    from src.models import FundTransfer
    from sqlalchemy import select, desc
    
    try:
        result = await session.execute(
            select(FundTransfer)
            .order_by(desc(FundTransfer.created_at))
            .limit(limit)
            .offset(offset)
        )
        transfers = result.scalars().all()
        
        return {
            "transfers": [
                {
                    "id": tfr.id,
                    "deposit_id": tfr.deposit_id,
                    "from_wallet": tfr.from_wallet,
                    "to_wallet": tfr.to_wallet,
                    "amount_usdc": tfr.amount_usdc,
                    "transaction_signature": tfr.transaction_signature,
                    "status": tfr.status,
                    "created_at": tfr.created_at.isoformat(),
                    "completed_at": tfr.completed_at.isoformat() if tfr.completed_at else None
                } for tfr in transfers
            ],
            "total": len(transfers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transfers: {str(e)}")

# Wallet-based User Management
@app.post("/api/wallet/connect")
async def connect_wallet(request: WalletConnectRequest, http_request: Request, session: AsyncSession = Depends(get_db)):
    """Connect user wallet and create/update user account"""
    from src.winner_tracking_service import winner_tracking_service
    
    # Check if wallet is blacklisted due to winner connections
    blacklist_check = await winner_tracking_service.is_wallet_blacklisted(session, request.wallet_address)
    
    if blacklist_check["blacklisted"]:
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "Wallet blacklisted",
                "reason": blacklist_check["reason"],
                "type": blacklist_check["type"]
            }
        )
    
    user_repo = UserRepository(session)
    
    # Check if user already exists
    existing_user = await get_user_by_wallet(request.wallet_address, session)
    
    if existing_user:
        # Update existing user
        await user_repo.update_user_wallet(
            existing_user.id, 
            request.wallet_address
        )
        user = existing_user
    else:
        # Create new user
        user, session_id = await get_or_create_user(http_request, session)
        await user_repo.update_user_wallet(
            user.id, 
            request.wallet_address
        )
    
    # Update display name if provided
    if request.display_name:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(display_name=request.display_name)
        )
        await session.commit()
    
    return {
        "success": True,
        "message": "Wallet connected successfully",
        "user_id": user.id,
        "wallet_address": request.wallet_address,
        "display_name": request.display_name
    }

@app.get("/api/user/profile/{wallet_address}")
async def get_user_profile(wallet_address: str, session: AsyncSession = Depends(get_db)):
    """Get user profile by wallet address"""
    user = await get_user_by_wallet(wallet_address, session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "wallet_address": user.wallet_address,
        "display_name": user.display_name,
        "created_at": user.created_at.isoformat(),
        "last_active": user.last_active.isoformat(),
        "total_attempts": user.total_attempts,
        "total_cost": user.total_cost,
        "wallet_connected_at": user.wallet_connected_at.isoformat() if user.wallet_connected_at else None
    }

@app.put("/api/user/profile/{wallet_address}")
async def update_user_profile(wallet_address: str, request: dict, session: AsyncSession = Depends(get_db)):
    """Update user profile"""
    user = await get_user_by_wallet(wallet_address, session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update display name
    if "display_name" in request:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(display_name=request["display_name"])
        )
        await session.commit()
    
    return {"message": "Profile updated successfully"}

@app.get("/api/user/stats/{wallet_address}")
async def get_user_statistics(wallet_address: str, session: AsyncSession = Depends(get_db)):
    """Get detailed user statistics and history"""
    user = await get_user_by_wallet(wallet_address, session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get conversation history
    conversations = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )
    conversation_list = conversations.scalars().all()
    
    # Get attack attempts
    attack_attempts = await session.execute(
        select(AttackAttempt)
        .where(AttackAttempt.user_id == user.id)
        .order_by(AttackAttempt.created_at.desc())
        .limit(100)
    )
    attempts_list = attack_attempts.scalars().all()
    
    # Get successful attempts (wins)
    successful_attempts = [a for a in attempts_list if a.success]
    
    # Get transaction history
    transactions = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(50)
    )
    transaction_list = transactions.scalars().all()
    
    # Calculate statistics
    total_wins = len(successful_attempts)
    total_prize_money = sum(t.amount for t in transaction_list if t.status == "completed")
    win_rate = (total_wins / user.total_attempts * 100) if user.total_attempts > 0 else 0
    
    # Recent activity (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_attempts = [a for a in attempts_list if a.created_at >= week_ago]
    
    return {
        "user_id": user.id,
        "wallet_address": user.wallet_address,
        "display_name": user.display_name,
        "created_at": user.created_at.isoformat(),
        "last_active": user.last_active.isoformat(),
        "statistics": {
            "total_attempts": user.total_attempts,
            "total_cost": user.total_cost,
            "total_wins": total_wins,
            "total_prize_money": total_prize_money,
            "win_rate": round(win_rate, 2),
            "recent_attempts": len(recent_attempts),
            "average_attempt_cost": round(user.total_cost / user.total_attempts, 4) if user.total_attempts > 0 else 0
        },
        "recent_conversations": [
            {
                "id": conv.id,
                "message": conv.user_message,
                "ai_response": conv.ai_response,
                "created_at": conv.created_at.isoformat(),
                "cost": conv.cost
            } for conv in conversation_list
        ],
        "recent_attempts": [
            {
                "id": attempt.id,
                "attempt_type": attempt.attempt_type,
                "success": attempt.success,
                "created_at": attempt.created_at.isoformat(),
                "cost": attempt.cost
            } for attempt in attempts_list[:20]  # Last 20 attempts
        ],
        "transaction_history": [
            {
                "id": tx.id,
                "amount": tx.amount,
                "token": tx.token,
                "status": tx.status,
                "created_at": tx.created_at.isoformat(),
                "transaction_hash": tx.transaction_hash
            } for tx in transaction_list
        ]
    }

@app.get("/api/user/achievements/{wallet_address}")
async def get_user_achievements(wallet_address: str, session: AsyncSession = Depends(get_db)):
    """Get user achievements and badges"""
    user = await get_user_by_wallet(wallet_address, session)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievements = []
    
    # Define achievement criteria
    if user.total_attempts >= 1:
        achievements.append({
            "id": "first_attempt",
            "name": "First Attempt",
            "description": "Made your first attempt to convince the AI",
            "unlocked_at": user.created_at.isoformat(),
            "icon": "🎯"
        })
    
    if user.total_attempts >= 10:
        achievements.append({
            "id": "persistent",
            "name": "Persistent",
            "description": "Made 10 attempts",
            "unlocked_at": user.last_active.isoformat(),
            "icon": "🔥"
        })
    
    if user.total_attempts >= 100:
        achievements.append({
            "id": "dedicated",
            "name": "Dedicated",
            "description": "Made 100 attempts",
            "unlocked_at": user.last_active.isoformat(),
            "icon": "💪"
        })
    
    # Check for wins
    successful_attempts = await session.execute(
        select(AttackAttempt)
        .where(AttackAttempt.user_id == user.id, AttackAttempt.success == True)
    )
    wins = successful_attempts.scalars().all()
    
    if len(wins) >= 1:
        achievements.append({
            "id": "first_win",
            "name": "First Victory",
            "description": "Successfully convinced the AI for the first time",
            "unlocked_at": wins[0].created_at.isoformat(),
            "icon": "🏆"
        })
    
    if len(wins) >= 5:
        achievements.append({
            "id": "master_manipulator",
            "name": "Master Manipulator",
            "description": "Successfully convinced the AI 5 times",
            "unlocked_at": wins[4].created_at.isoformat(),
            "icon": "🎭"
        })
    
    # High value wins
    transactions = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id, Transaction.status == "completed")
    )
    completed_txs = transactions.scalars().all()
    
    if any(tx.amount >= 1000 for tx in completed_txs):
        achievements.append({
            "id": "big_winner",
            "name": "Big Winner",
            "description": "Won a prize worth $1000 or more",
            "unlocked_at": max(tx.created_at for tx in completed_txs if tx.amount >= 1000).isoformat(),
            "icon": "💰"
        })
    
    return {
        "user_id": user.id,
        "wallet_address": user.wallet_address,
        "achievements": achievements,
        "total_achievements": len(achievements)
    }

# Leaderboards
@app.get("/api/leaderboards/top-winners")
async def get_top_winners(session: AsyncSession = Depends(get_db)):
    """Get leaderboard of users with most wins"""
    # Get users with their win counts
    result = await session.execute(
        select(
            User.id,
            User.wallet_address,
            User.display_name,
            User.created_at,
            func.count(AttackAttempt.id).label('win_count')
        )
        .join(AttackAttempt, User.id == AttackAttempt.user_id)
        .where(AttackAttempt.success == True)
        .group_by(User.id, User.wallet_address, User.display_name, User.created_at)
        .order_by(func.count(AttackAttempt.id).desc())
        .limit(50)
    )
    
    winners = result.all()
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": winner.id,
                "wallet_address": winner.wallet_address,
                "display_name": winner.display_name or f"User {winner.wallet_address[:8]}...",
                "win_count": winner.win_count,
                "joined_at": winner.created_at.isoformat()
            }
            for i, winner in enumerate(winners)
        ],
        "total_entries": len(winners)
    }

@app.get("/api/leaderboards/top-spenders")
async def get_top_spenders(session: AsyncSession = Depends(get_db)):
    """Get leaderboard of users who spent the most"""
    result = await session.execute(
        select(User)
        .where(User.total_cost > 0)
        .order_by(User.total_cost.desc())
        .limit(50)
    )
    
    spenders = result.scalars().all()
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": spender.id,
                "wallet_address": spender.wallet_address,
                "display_name": spender.display_name or f"User {spender.wallet_address[:8]}...",
                "total_spent": spender.total_cost,
                "total_attempts": spender.total_attempts,
                "average_per_attempt": round(spender.total_cost / spender.total_attempts, 4) if spender.total_attempts > 0 else 0
            }
            for i, spender in enumerate(spenders)
        ],
        "total_entries": len(spenders)
    }

@app.get("/api/leaderboards/recent-winners")
async def get_recent_winners(session: AsyncSession = Depends(get_db)):
    """Get recent winners with their prize amounts"""
    # Get recent successful attempts with transaction details
    result = await session.execute(
        select(
            AttackAttempt.id,
            AttackAttempt.created_at,
            AttackAttempt.additional_data,
            User.wallet_address,
            User.display_name,
            Transaction.amount,
            Transaction.token
        )
        .join(User, AttackAttempt.user_id == User.id)
        .outerjoin(Transaction, AttackAttempt.id == Transaction.attack_attempt_id)
        .where(AttackAttempt.success == True)
        .order_by(AttackAttempt.created_at.desc())
        .limit(20)
    )
    
    recent_wins = result.all()
    
    return {
        "recent_winners": [
            {
                "attempt_id": win.id,
                "wallet_address": win.wallet_address,
                "display_name": win.display_name or f"User {win.wallet_address[:8]}...",
                "prize_amount": win.amount or 0,
                "token": win.token or "SOL",
                "won_at": win.created_at.isoformat(),
                "transaction_data": win.additional_data
            }
            for win in recent_wins
        ],
        "total_entries": len(recent_wins)
    }

@app.get("/api/leaderboards/win-rate")
async def get_win_rate_leaderboard(session: AsyncSession = Depends(get_db)):
    """Get leaderboard by win rate (minimum 10 attempts)"""
    # Get users with at least 10 attempts and calculate win rate
    result = await session.execute(
        select(
            User.id,
            User.wallet_address,
            User.display_name,
            User.total_attempts,
            User.total_cost,
            func.count(AttackAttempt.id).label('win_count')
        )
        .outerjoin(AttackAttempt, and_(
            User.id == AttackAttempt.user_id,
            AttackAttempt.success == True
        ))
        .where(User.total_attempts >= 10)
        .group_by(User.id, User.wallet_address, User.display_name, User.total_attempts, User.total_cost)
        .having(func.count(AttackAttempt.id) > 0)  # Only users with at least one win
        .order_by((func.count(AttackAttempt.id) / User.total_attempts).desc())
        .limit(50)
    )
    
    win_rate_users = result.all()
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": user.id,
                "wallet_address": user.wallet_address,
                "display_name": user.display_name or f"User {user.wallet_address[:8]}...",
                "win_count": user.win_count,
                "total_attempts": user.total_attempts,
                "win_rate": round((user.win_count / user.total_attempts) * 100, 2),
                "total_spent": user.total_cost
            }
            for i, user in enumerate(win_rate_users)
        ],
        "total_entries": len(win_rate_users)
    }

@app.get("/api/leaderboards/stats")
async def get_leaderboard_stats(session: AsyncSession = Depends(get_db)):
    """Get overall leaderboard statistics"""
    # Total users
    total_users = await session.execute(select(func.count(User.id)))
    total_users_count = total_users.scalar()
    
    # Total attempts
    total_attempts = await session.execute(select(func.count(AttackAttempt.id)))
    total_attempts_count = total_attempts.scalar()
    
    # Total wins
    total_wins = await session.execute(
        select(func.count(AttackAttempt.id))
        .where(AttackAttempt.success == True)
    )
    total_wins_count = total_wins.scalar()
    
    # Total prize money distributed
    total_prize_money = await session.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.status == "completed")
    )
    total_prize_amount = total_prize_money.scalar() or 0
    
    # Average win rate
    overall_win_rate = (total_wins_count / total_attempts_count * 100) if total_attempts_count > 0 else 0
    
    return {
        "total_users": total_users_count,
        "total_attempts": total_attempts_count,
        "total_wins": total_wins_count,
        "total_prize_money": total_prize_amount,
        "overall_win_rate": round(overall_win_rate, 2),
        "average_attempts_per_user": round(total_attempts_count / total_users_count, 2) if total_users_count > 0 else 0
    }

# Analytics Dashboard
@app.get("/api/analytics/overview")
async def get_analytics_overview(session: AsyncSession = Depends(get_db)):
    """Get comprehensive analytics overview"""
    # Basic stats
    total_users = await session.execute(select(func.count(User.id)))
    total_users_count = total_users.scalar()
    
    total_attempts = await session.execute(select(func.count(AttackAttempt.id)))
    total_attempts_count = total_attempts.scalar()
    
    total_wins = await session.execute(
        select(func.count(AttackAttempt.id))
        .where(AttackAttempt.success == True)
    )
    total_wins_count = total_wins.scalar()
    
    total_revenue = await session.execute(select(func.sum(User.total_cost)))
    total_revenue_amount = total_revenue.scalar() or 0
    
    total_prize_money = await session.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.status == "completed")
    )
    total_prize_amount = total_prize_money.scalar() or 0
    
    # Time-based stats (last 24 hours)
    from datetime import timedelta
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    recent_attempts = await session.execute(
        select(func.count(AttackAttempt.id))
        .where(AttackAttempt.created_at >= day_ago)
    )
    recent_attempts_count = recent_attempts.scalar()
    
    recent_wins = await session.execute(
        select(func.count(AttackAttempt.id))
        .where(AttackAttempt.success == True, AttackAttempt.created_at >= day_ago)
    )
    recent_wins_count = recent_wins.scalar()
    
    recent_revenue = await session.execute(
        select(func.sum(AttackAttempt.cost))
        .where(AttackAttempt.created_at >= day_ago)
    )
    recent_revenue_amount = recent_revenue.scalar() or 0
    
    return {
        "overview": {
            "total_users": total_users_count,
            "total_attempts": total_attempts_count,
            "total_wins": total_wins_count,
            "total_revenue": total_revenue_amount,
            "total_prize_money": total_prize_amount,
            "net_profit": total_revenue_amount - total_prize_amount,
            "overall_win_rate": round((total_wins_count / total_attempts_count * 100), 2) if total_attempts_count > 0 else 0
        },
        "last_24h": {
            "attempts": recent_attempts_count,
            "wins": recent_wins_count,
            "revenue": recent_revenue_amount,
            "win_rate": round((recent_wins_count / recent_attempts_count * 100), 2) if recent_attempts_count > 0 else 0
        }
    }

@app.get("/api/analytics/user-behavior")
async def get_user_behavior_analytics(session: AsyncSession = Depends(get_db)):
    """Get user behavior analytics"""
    # User activity distribution
    activity_levels = await session.execute(
        select(
            func.case(
                (User.total_attempts == 0, "inactive"),
                (User.total_attempts.between(1, 5), "low"),
                (User.total_attempts.between(6, 20), "medium"),
                (User.total_attempts.between(21, 100), "high"),
                else_="very_high"
            ).label('activity_level'),
            func.count(User.id).label('user_count')
        )
        .group_by('activity_level')
    )
    
    activity_distribution = {row.activity_level: row.user_count for row in activity_levels.all()}
    
    # Average session length (conversations per user)
    avg_conversations = await session.execute(
        select(func.avg(func.count(Conversation.id)))
        .join(User, Conversation.user_id == User.id)
        .group_by(User.id)
    )
    avg_conversations_per_user = avg_conversations.scalar() or 0
    
    # Most common attempt types
    attempt_types = await session.execute(
        select(
            AttackAttempt.attempt_type,
            func.count(AttackAttempt.id).label('count')
        )
        .group_by(AttackAttempt.attempt_type)
        .order_by(func.count(AttackAttempt.id).desc())
        .limit(10)
    )
    
    common_attempts = [
        {"type": row.attempt_type, "count": row.count}
        for row in attempt_types.all()
    ]
    
    # User retention (users who made attempts in last 7 days vs total)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await session.execute(
        select(func.count(func.distinct(AttackAttempt.user_id)))
        .where(AttackAttempt.created_at >= week_ago)
    )
    active_users_count = active_users.scalar()
    
    return {
        "activity_distribution": activity_distribution,
        "avg_conversations_per_user": round(avg_conversations_per_user, 2),
        "common_attempt_types": common_attempts,
        "user_retention": {
            "active_users_7d": active_users_count,
            "retention_rate": round((active_users_count / total_users_count * 100), 2) if total_users_count > 0 else 0
        }
    }

@app.get("/api/analytics/financial")
async def get_financial_analytics(session: AsyncSession = Depends(get_db)):
    """Get financial analytics"""
    # Revenue over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_revenue = await session.execute(
        select(
            func.date(AttackAttempt.created_at).label('date'),
            func.sum(AttackAttempt.cost).label('revenue')
        )
        .where(AttackAttempt.created_at >= thirty_days_ago)
        .group_by(func.date(AttackAttempt.created_at))
        .order_by(func.date(AttackAttempt.created_at))
    )
    
    revenue_timeline = [
        {"date": row.date.isoformat(), "revenue": float(row.revenue or 0)}
        for row in daily_revenue.all()
    ]
    
    # Prize payouts over time
    daily_payouts = await session.execute(
        select(
            func.date(Transaction.created_at).label('date'),
            func.sum(Transaction.amount).label('payouts')
        )
        .where(Transaction.status == "completed", Transaction.created_at >= thirty_days_ago)
        .group_by(func.date(Transaction.created_at))
        .order_by(func.date(Transaction.created_at))
    )
    
    payout_timeline = [
        {"date": row.date.isoformat(), "payouts": float(row.payouts or 0)}
        for row in daily_payouts.all()
    ]
    
    # Top earning users
    top_earners = await session.execute(
        select(
            User.wallet_address,
            User.display_name,
            func.sum(Transaction.amount).label('total_earned')
        )
        .join(Transaction, User.id == Transaction.user_id)
        .where(Transaction.status == "completed")
        .group_by(User.id, User.wallet_address, User.display_name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(10)
    )
    
    top_earners_list = [
        {
            "wallet_address": row.wallet_address,
            "display_name": row.display_name or f"User {row.wallet_address[:8]}...",
            "total_earned": float(row.total_earned or 0)
        }
        for row in top_earners.all()
    ]
    
    return {
        "revenue_timeline": revenue_timeline,
        "payout_timeline": payout_timeline,
        "top_earners": top_earners_list
    }

@app.get("/api/analytics/ai-performance")
async def get_ai_performance_analytics(session: AsyncSession = Depends(get_db)):
    """Get AI performance and resistance analytics"""
    # Win rate over time
    daily_win_rates = await session.execute(
        select(
            func.date(AttackAttempt.created_at).label('date'),
            func.count(AttackAttempt.id).label('total_attempts'),
            func.sum(func.case((AttackAttempt.success == True, 1), else_=0)).label('wins')
        )
        .where(AttackAttempt.created_at >= datetime.utcnow() - timedelta(days=30))
        .group_by(func.date(AttackAttempt.created_at))
        .order_by(func.date(AttackAttempt.created_at))
    )
    
    win_rate_timeline = []
    for row in daily_win_rates.all():
        win_rate = (row.wins / row.total_attempts * 100) if row.total_attempts > 0 else 0
        win_rate_timeline.append({
            "date": row.date.isoformat(),
            "total_attempts": row.total_attempts,
            "wins": row.wins,
            "win_rate": round(win_rate, 2)
        })
    
    # Most successful manipulation types
    successful_attempts = await session.execute(
        select(
            AttackAttempt.attempt_type,
            func.count(AttackAttempt.id).label('total_attempts'),
            func.sum(func.case((AttackAttempt.success == True, 1), else_=0)).label('wins')
        )
        .group_by(AttackAttempt.attempt_type)
        .having(func.count(AttackAttempt.id) >= 5)  # Only types with at least 5 attempts
        .order_by((func.sum(func.case((AttackAttempt.success == True, 1), else_=0)) / func.count(AttackAttempt.id)).desc())
    )
    
    successful_types = []
    for row in successful_attempts.all():
        success_rate = (row.wins / row.total_attempts * 100) if row.total_attempts > 0 else 0
        successful_types.append({
            "type": row.attempt_type,
            "total_attempts": row.total_attempts,
            "wins": row.wins,
            "success_rate": round(success_rate, 2)
        })
    
    # AI resistance strength (average cost per attempt)
    resistance_analysis = await session.execute(
        select(
            func.avg(AttackAttempt.cost).label('avg_cost'),
            func.min(AttackAttempt.cost).label('min_cost'),
            func.max(AttackAttempt.cost).label('max_cost')
        )
    )
    
    resistance_stats = resistance_analysis.first()
    
    return {
        "win_rate_timeline": win_rate_timeline,
        "successful_manipulation_types": successful_types,
        "ai_resistance": {
            "avg_cost_per_attempt": round(float(resistance_stats.avg_cost or 0), 4),
            "min_cost": float(resistance_stats.min_cost or 0),
            "max_cost": float(resistance_stats.max_cost or 0)
        }
    }

@app.get("/api/analytics/security")
async def get_security_analytics(session: AsyncSession = Depends(get_db)):
    """Get security and attack analytics"""
    # Blacklisted phrases usage
    blacklist_usage = await session.execute(
        select(
            BlacklistedPhrase.phrase,
            BlacklistedPhrase.usage_count,
            BlacklistedPhrase.created_at
        )
        .order_by(BlacklistedPhrase.usage_count.desc())
        .limit(20)
    )
    
    top_blacklisted = [
        {
            "phrase": row.phrase,
            "usage_count": row.usage_count,
            "created_at": row.created_at.isoformat()
        }
        for row in blacklist_usage.all()
    ]
    
    # Attack patterns over time
    attack_timeline = await session.execute(
        select(
            func.date(AttackAttempt.created_at).label('date'),
            func.count(AttackAttempt.id).label('total_attempts'),
            func.sum(func.case((AttackAttempt.success == True, 1), else_=0)).label('successful_attacks')
        )
        .where(AttackAttempt.created_at >= datetime.utcnow() - timedelta(days=7))
        .group_by(func.date(AttackAttempt.created_at))
        .order_by(func.date(AttackAttempt.created_at))
    )
    
    attack_timeline_data = []
    for row in attack_timeline.all():
        success_rate = (row.successful_attacks / row.total_attempts * 100) if row.total_attempts > 0 else 0
        attack_timeline_data.append({
            "date": row.date.isoformat(),
            "total_attempts": row.total_attempts,
            "successful_attacks": row.successful_attacks,
            "success_rate": round(success_rate, 2)
        })
    
    # Most persistent attackers
    persistent_attackers = await session.execute(
        select(
            User.wallet_address,
            User.display_name,
            func.count(AttackAttempt.id).label('total_attempts'),
            func.sum(func.case((AttackAttempt.success == True, 1), else_=0)).label('wins')
        )
        .join(AttackAttempt, User.id == AttackAttempt.user_id)
        .group_by(User.id, User.wallet_address, User.display_name)
        .having(func.count(AttackAttempt.id) >= 10)
        .order_by(func.count(AttackAttempt.id).desc())
        .limit(10)
    )
    
    top_attackers = [
        {
            "wallet_address": row.wallet_address,
            "display_name": row.display_name or f"User {row.wallet_address[:8]}...",
            "total_attempts": row.total_attempts,
            "wins": row.wins,
            "success_rate": round((row.wins / row.total_attempts * 100), 2) if row.total_attempts > 0 else 0
        }
        for row in persistent_attackers.all()
    ]
    
    return {
        "top_blacklisted_phrases": top_blacklisted,
        "attack_timeline": attack_timeline_data,
        "persistent_attackers": top_attackers
    }

# Winner Tracking System
@app.get("/api/winners/list")
async def get_winners_list(session: AsyncSession = Depends(get_db), limit: int = 50):
    """Get list of all winners"""
    from src.winner_tracking_service import winner_tracking_service
    
    winners = await winner_tracking_service.get_winner_list(session, limit)
    return {
        "winners": winners,
        "total": len(winners)
    }

@app.get("/api/winners/stats")
async def get_winner_statistics(session: AsyncSession = Depends(get_db)):
    """Get winner tracking statistics"""
    from src.winner_tracking_service import winner_tracking_service
    
    stats = await winner_tracking_service.get_winner_statistics(session)
    return stats

@app.post("/api/winners/check-wallet")
async def check_wallet_blacklist(request: dict, session: AsyncSession = Depends(get_db)):
    """Check if a wallet is blacklisted due to winner connections"""
    from src.winner_tracking_service import winner_tracking_service
    
    wallet_address = request.get("wallet_address")
    if not wallet_address:
        raise HTTPException(status_code=400, detail="wallet_address is required")
    
    blacklist_status = await winner_tracking_service.is_wallet_blacklisted(session, wallet_address)
    return blacklist_status

@app.post("/api/winners/record-funding")
async def record_wallet_funding(request: dict, session: AsyncSession = Depends(get_db)):
    """Record wallet funding source for tracking"""
    from src.winner_tracking_service import winner_tracking_service
    
    wallet_address = request.get("wallet_address")
    funding_source = request.get("funding_source")
    amount = request.get("amount", 0.0)
    
    if not wallet_address or not funding_source:
        raise HTTPException(status_code=400, detail="wallet_address and funding_source are required")
    
    await winner_tracking_service.record_wallet_funding(session, wallet_address, funding_source, amount)
    return {"message": "Funding source recorded successfully"}

@app.post("/api/winners/activate-tracking")
async def activate_winner_tracking(session: AsyncSession = Depends(get_db)):
    """Manually activate winner tracking (for testing)"""
    from src.winner_tracking_service import winner_tracking_service
    
    await winner_tracking_service.activate_winner_tracking(session)
    return {"message": "Winner tracking activated"}

@app.get("/api/winners/connected-wallets/{winner_id}")
async def get_connected_wallets(winner_id: int, session: AsyncSession = Depends(get_db)):
    """Get wallets connected to a specific winner"""
    from src.models import ConnectedWallet
    
    connected_wallets = await session.execute(
        select(ConnectedWallet)
        .where(ConnectedWallet.winner_id == winner_id)
        .order_by(ConnectedWallet.discovered_at.desc())
    )
    
    wallets = []
    for wallet in connected_wallets.scalars().all():
        wallets.append({
            "id": wallet.id,
            "wallet_address": wallet.wallet_address,
            "connection_type": wallet.connection_type,
            "connection_details": wallet.connection_details,
            "discovered_at": wallet.discovered_at.isoformat(),
            "is_blacklisted": wallet.is_blacklisted
        })
    
    return {
        "winner_id": winner_id,
        "connected_wallets": wallets,
        "total": len(wallets)
    }

# Referral System Endpoints
@app.get("/api/referral/code/{user_id}")
async def get_referral_code(user_id: int, session: AsyncSession = Depends(get_db)):
    """Get or create referral code for a user"""
    try:
        referral_code = await referral_service.get_or_create_referral_code(session, user_id)
        return {
            "success": True,
            "referral_code": referral_code.referral_code,
            "created_at": referral_code.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get referral code: {str(e)}")

@app.post("/api/referral/process")
async def process_referral_signup(request: dict, session: AsyncSession = Depends(get_db)):
    """Process a referral signup when a new user makes their first deposit"""
    try:
        referee_user_id = request.get("referee_user_id")
        referral_code = request.get("referral_code")
        wallet_address = request.get("wallet_address")
        email = request.get("email")
        
        if not referee_user_id or not referral_code:
            raise HTTPException(status_code=400, detail="referee_user_id and referral_code are required")
        
        result = await referral_service.process_referral_signup(
            session, referee_user_id, referral_code, wallet_address, email
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process referral: {str(e)}")

@app.get("/api/referral/stats/{user_id}")
async def get_referral_stats(user_id: int, session: AsyncSession = Depends(get_db)):
    """Get referral statistics for a user"""
    try:
        stats = await referral_service.get_referral_stats(session, user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get referral stats: {str(e)}")

@app.get("/api/referral/leaderboard")
async def get_referral_leaderboard(session: AsyncSession = Depends(get_db), limit: int = 50):
    """Get referral leaderboard"""
    try:
        leaderboard = await referral_service.get_referral_leaderboard(session, limit)
        return {
            "leaderboard": leaderboard,
            "total": len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get referral leaderboard: {str(e)}")

@app.get("/api/referral/free-questions/{user_id}")
async def get_free_questions(user_id: int, session: AsyncSession = Depends(get_db)):
    """Get free questions available for a user"""
    try:
        free_questions = await referral_service.get_user_free_questions(session, user_id)
        return {
            "user_id": user_id,
            "free_questions_available": free_questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get free questions: {str(e)}")

@app.post("/api/referral/use-free-question")
async def use_free_question(request: dict, session: AsyncSession = Depends(get_db)):
    """Use one free question for a user"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        success = await referral_service.use_free_question(session, user_id)
        return {
            "success": success,
            "message": "Free question used successfully" if success else "No free questions available"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to use free question: {str(e)}")

# Research Fund Endpoints
@app.get("/api/research/status")
async def get_research_fund_status(session: AsyncSession = Depends(get_db)):
    """Get current research fund status"""
    try:
        status = await research_service.get_research_status(session)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research status: {str(e)}")

@app.post("/api/research/attempt")
async def process_research_attempt(request: dict, session: AsyncSession = Depends(get_db)):
    """Process a research attempt"""
    try:
        user_id = request.get("user_id")
        message_content = request.get("message_content")
        ai_response = request.get("ai_response")
        
        if not all([user_id, message_content, ai_response]):
            raise HTTPException(status_code=400, detail="user_id, message_content, and ai_response are required")
        
        result = await research_service.process_research_attempt(
            session, user_id, message_content, ai_response
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process research attempt: {str(e)}")

@app.post("/api/research/success")
async def determine_research_success(request: dict, session: AsyncSession = Depends(get_db)):
    """Determine if research attempt was successful"""
    try:
        user_id = request.get("user_id")
        entry_id = request.get("entry_id")
        should_transfer = request.get("should_transfer", False)
        
        if not all([user_id, entry_id]):
            raise HTTPException(status_code=400, detail="user_id and entry_id are required")
        
        result = await research_service.determine_research_success(
            session, user_id, entry_id, should_transfer
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to determine research success: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
