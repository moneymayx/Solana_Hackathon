'use client';

/**
 * V3 Testing Page
 * 
 * Dedicated page for testing V3 contract functionality
 * Visit: http://localhost:3000/test-v3
 */

import { useState, useEffect } from 'react';
import V3PaymentButton from '@/components/V3PaymentButton';
import PaymentMethodSelector from '@/components/PaymentMethodSelector';
import WalletButton from '@/components/WalletButton';
import { useWallet } from '@solana/wallet-adapter-react';
import { CheckCircle, XCircle, AlertCircle, Wallet } from 'lucide-react';

export default function TestV3Page() {
  const { connected, publicKey } = useWallet();
  const [isMounted, setIsMounted] = useState(false);
  const [testResults, setTestResults] = useState<{
    envCheck: boolean | null;
    componentCheck: boolean | null;
    paymentTest: boolean | null;
  }>({
    envCheck: null,
    componentCheck: null,
    paymentTest: null,
  });

  // Fix hydration mismatch - only render wallet-dependent UI after mount
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Check environment variable (client-side check)
  // Note: Next.js embeds NEXT_PUBLIC_ vars at build time
  const checkEnvironment = () => {
    const rawValue = process.env.NEXT_PUBLIC_USE_CONTRACT_V3;
    const useV3 = rawValue === 'true';
    
    console.log('🔍 Environment Variable Check:');
    console.log('  Raw value:', rawValue);
    console.log('  Type:', typeof rawValue);
    console.log('  Evaluated (=== "true"):', useV3);
    console.log('  All env vars with NEXT_PUBLIC_USE_CONTRACT:', {
      V3: process.env.NEXT_PUBLIC_USE_CONTRACT_V3,
      V2: process.env.NEXT_PUBLIC_USE_CONTRACT_V2,
    });
    
    // More specific check: Only look within the payment component containers
    // Avoid false positives from page documentation text
    const paymentContainers = document.querySelectorAll('[class*="PaymentMethodSelector"], [class*="v3-payment-button"], [class*="v2-payment-button"]');
    let hasV3Badge = false;
    const foundElements: Element[] = [];
    
    paymentContainers.forEach(container => {
      const badge = Array.from(container.querySelectorAll('*')).find(
        el => el.textContent?.includes('🔒 Using V3') && !el.closest('[class*="bg-gray-800"]')
      );
      if (badge) {
        hasV3Badge = true;
        foundElements.push(badge);
      }
    });
    
    // Also check what PaymentMethodSelector actually sees
    const paymentSelectorDivs = Array.from(document.querySelectorAll('div')).filter(
      div => {
        const children = Array.from(div.children);
        return children.some(child => 
          child.textContent?.includes('Payment Amount') || 
          child.textContent?.includes('Pay')
        );
      }
    );
    
    console.log('🔍 Component Analysis:');
    console.log('  Payment containers found:', paymentContainers.length);
    console.log('  Payment form divs found:', paymentSelectorDivs.length);
    console.log('  V3 badge found:', hasV3Badge);
    if (foundElements.length > 0) {
      console.log('  Badge elements:', foundElements);
    }
    
    // Check if V3PaymentButton is actually rendered (more reliable)
    const hasV3Button = document.querySelector('[class*="v3-payment-button"]') !== null;
    const hasV2Button = document.querySelector('[class*="v2-payment-button"]') !== null;
    
    console.log('  V3PaymentButton rendered:', hasV3Button);
    console.log('  V2PaymentButton rendered:', hasV2Button);
    
    // Real check: Is V3 actually being used?
    const actuallyWorking = hasV3Badge && hasV3Button && !hasV2Button;
    
    setTestResults(prev => ({ 
      ...prev, 
      envCheck: actuallyWorking
    }));
    
    if (actuallyWorking) {
      console.log('✅ V3 IS WORKING! (V3PaymentButton rendered with badge)');
    } else if (useV3 && !hasV3Button) {
      console.warn('⚠️ Env var says V3, but V3PaymentButton not rendered');
      console.log('  - Env var:', rawValue);
      console.log('  - This means Next.js did not pick up the env var');
      console.log('  - Fix: Restart dev server after adding to .env.local');
    } else if (!useV3) {
      console.warn('❌ V3 NOT ENABLED');
      console.log('  - Env var is:', rawValue === undefined ? 'undefined (not set)' : rawValue);
      console.log('  - PaymentMethodSelector will render V2PaymentButton');
      console.log('  - To enable V3:');
      console.log('    1. Create/update frontend/.env.local');
      console.log('    2. Add: NEXT_PUBLIC_USE_CONTRACT_V3=true');
      console.log('    3. Add: NEXT_PUBLIC_USE_CONTRACT_V2=false');
      console.log('    4. Restart dev server (Ctrl+C then npm run dev)');
      console.log('    5. Hard refresh browser (Ctrl+Shift+R)');
    }
  };

  // Check if V3 components are rendering
  const checkComponents = () => {
    // Specific check: Look for V3 badge within payment components only
    const paymentContainers = document.querySelectorAll('[class*="PaymentMethodSelector"], [class*="v3-payment-button"], [class*="v2-payment-button"]');
    let hasV3Badge = false;
    
    paymentContainers.forEach(container => {
      // Only check within the container, not the whole page
      // Use Array.find to search text content properly (querySelector doesn't support :has-text)
      const allElements = Array.from(container.querySelectorAll('*'));
      const badge = allElements.find(
        el => {
          const text = el.textContent?.trim() || '';
          // Check for exact badge text or contains the lock emoji with V3
          const hasV3Text = text === '🔒 Using V3 (Secure)' || text.includes('🔒 Using V3');
          
          if (!hasV3Text) return false;
          
          // Exclude elements inside documentation/instruction sections (gray boxes that aren't payment components)
          const isInInstructions = el.closest('[class*="bg-gray-800"]:not([class*="v3-payment"]):not([class*="v2-payment"]):not([class*="PaymentMethodSelector"])');
          
          return !isInInstructions;
        }
      );
      if (badge) {
        hasV3Badge = true;
        console.log('✅ Found V3 badge in:', container, badge);
      }
    });
    
    // Also check what's actually rendered
    const v3Button = document.querySelector('[class*="v3-payment-button"]');
    const v2Button = document.querySelector('[class*="v2-payment-button"]');
    
    console.log('🔍 Component Check:');
    console.log('  V3PaymentButton element:', v3Button ? 'Found ✅' : 'Not found ❌');
    console.log('  V2PaymentButton element:', v2Button ? 'Found (V2 active)' : 'Not found');
    console.log('  V3 badge found:', hasV3Badge);
    
    setTestResults(prev => ({ ...prev, componentCheck: hasV3Badge && !!v3Button && !v2Button }));
    
    if (hasV3Badge && v3Button && !v2Button) {
      console.log('✅ V3 components detected and active');
    } else if (v2Button) {
      console.warn('⚠️ V2 components detected instead of V3');
      console.log('💡 PaymentMethodSelector is rendering V2PaymentButton');
      console.log('💡 This means NEXT_PUBLIC_USE_CONTRACT_V3 is not set or not "true"');
    } else {
      console.warn('⚠️ V3 components not detected');
      console.log('💡 Make sure NEXT_PUBLIC_USE_CONTRACT_V3=true and restart dev server');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">V3 Contract Testing</h1>
              <p className="text-gray-400">
                Test V3 smart contract functionality on the frontend
              </p>
            </div>
            <div className="flex items-center gap-3">
              {isMounted && connected && publicKey && (
                <div className="text-right">
                  <div className="text-sm text-gray-400">Wallet Connected</div>
                  <div className="text-sm text-green-400 font-mono truncate max-w-[200px]">
                    {publicKey.toBase58().slice(0, 8)}...{publicKey.toBase58().slice(-6)}
                  </div>
                </div>
              )}
              {isMounted && <WalletButton />}
              {!isMounted && (
                <div className="h-[40px] w-[200px] bg-gray-700 rounded animate-pulse" />
              )}
            </div>
          </div>
          
          {isMounted && !connected && (
            <div className="bg-blue-900/20 border border-blue-500 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3">
                <Wallet className="h-5 w-5 text-blue-400" />
                <div>
                  <p className="text-blue-400 font-medium">Connect Your Wallet</p>
                  <p className="text-sm text-gray-300 mt-1">
                    Click the button above to connect your Solana wallet (Phantom, Solflare, etc.) to test payments
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Checks */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-xl font-bold text-white mb-4">Quick Checks</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Environment Variable Check</span>
              <div className="flex items-center gap-2">
                {testResults.envCheck === true && (
                  <>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="text-green-400">V3 Active</span>
                  </>
                )}
                {testResults.envCheck === false && (
                  <>
                    <XCircle className="h-5 w-5 text-red-500" />
                    <span className="text-red-400">V3 Not Detected</span>
                  </>
                )}
                {testResults.envCheck === null && (
                  <span className="text-gray-500">Not checked</span>
                )}
                <button
                  onClick={checkEnvironment}
                  className="ml-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
                >
                  Check
                </button>
              </div>
            </div>
            {testResults.envCheck === false && (
              <div className="mt-2 text-xs text-yellow-400 bg-yellow-900/20 p-3 rounded">
                <p><strong>Note:</strong> Next.js embeds env vars at build time.</p>
                <p>Even if this shows "Not Detected", V3 might still work.</p>
                <p className="mt-1"><strong>Better test:</strong> Look for "🔒 Using V3 (Secure)" badge below - that's the real indicator!</p>
              </div>
            )}
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Component Rendering Check</span>
              <div className="flex items-center gap-2">
                {testResults.componentCheck === true && (
                  <>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="text-green-400">V3 Components Found</span>
                  </>
                )}
                {testResults.componentCheck === false && (
                  <>
                    <XCircle className="h-5 w-5 text-red-500" />
                    <span className="text-red-400">V3 Components Not Found</span>
                  </>
                )}
                {testResults.componentCheck === null && (
                  <span className="text-gray-500">Not checked</span>
                )}
                <button
                  onClick={checkComponents}
                  className="ml-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
                >
                  Check
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration Info */}
        <div className="bg-blue-900/20 border border-blue-500 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-bold text-blue-400 mb-3 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Setup Instructions
          </h3>
          <div className="space-y-2 text-gray-300 text-sm">
            <p><strong>1. Frontend (.env.local):</strong></p>
            <code className="block bg-gray-900 px-3 py-2 rounded mt-1">
              NEXT_PUBLIC_USE_CONTRACT_V3=true
              <br />
              NEXT_PUBLIC_USE_CONTRACT_V2=false
            </code>
            <p className="mt-3"><strong>2. Backend (.env):</strong></p>
            <code className="block bg-gray-900 px-3 py-2 rounded mt-1">
              USE_CONTRACT_V3=true
              <br />
              USE_CONTRACT_V2=false
            </code>
            <p className="mt-3"><strong>3. Restart both servers after changing .env files</strong></p>
          </div>
        </div>

        {/* Debug Info */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-xl font-bold text-white mb-4">🔍 Current Status</h2>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">Env Var (process.env):</span>
              <code className="bg-gray-900 px-2 py-1 rounded text-yellow-400">
                {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === 'true' ? 'true ✅' : 
                 process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === undefined ? 'undefined ❌' : 
                 `${process.env.NEXT_PUBLIC_USE_CONTRACT_V3} ⚠️`}
              </code>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">PaymentMethodSelector will render:</span>
              <code className="bg-gray-900 px-2 py-1 rounded">
                {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === 'true' ? 
                  <span className="text-green-400">V3PaymentButton ✅</span> : 
                  <span className="text-orange-400">V2PaymentButton (V3 not enabled)</span>}
              </code>
            </div>
            {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 !== 'true' && (
              <div className="mt-3 p-3 bg-red-900/20 border border-red-500 rounded text-red-400 text-xs">
                <p className="font-bold mb-1">⚠️ V3 is NOT enabled</p>
                <p className="mb-2">The env var is {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === undefined ? 'undefined' : 'not set to "true"'}</p>
                <p className="mb-1"><strong>To fix:</strong></p>
                <ol className="list-decimal list-inside ml-2 space-y-1">
                  <li>Create/update <code className="bg-gray-900 px-1 rounded">frontend/.env.local</code></li>
                  <li>Add: <code className="bg-gray-900 px-1 rounded">NEXT_PUBLIC_USE_CONTRACT_V3=true</code></li>
                  <li>Add: <code className="bg-gray-900 px-1 rounded">NEXT_PUBLIC_USE_CONTRACT_V2=false</code></li>
                  <li>Stop dev server (Ctrl+C)</li>
                  <li>Restart: <code className="bg-gray-900 px-1 rounded">npm run dev</code></li>
                  <li>Hard refresh browser (Ctrl+Shift+R)</li>
                </ol>
              </div>
            )}
          </div>
        </div>

        {/* Test Components */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* PaymentMethodSelector (Auto-routing) */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">
              PaymentMethodSelector
            </h2>
            <p className="text-sm text-gray-400 mb-4">
              Automatically uses V3 when flag is enabled
            </p>
            <PaymentMethodSelector
              defaultAmount={10}
              onSuccess={(sig, url) => {
                console.log('✅ PaymentMethodSelector success:', sig, url);
                setTestResults(prev => ({ ...prev, paymentTest: true }));
              }}
              onError={(err) => {
                console.error('❌ PaymentMethodSelector error:', err);
                setTestResults(prev => ({ ...prev, paymentTest: false }));
              }}
            />
          </div>

          {/* Direct V3PaymentButton */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">
              V3PaymentButton (Direct)
            </h2>
            <p className="text-sm text-gray-400 mb-4">
              Direct V3 component (always uses V3)
            </p>
            <V3PaymentButton
              defaultAmount={10}
              onSuccess={(sig, url) => {
                console.log('✅ V3PaymentButton success:', sig, url);
                setTestResults(prev => ({ ...prev, paymentTest: true }));
              }}
              onError={(err) => {
                console.error('❌ V3PaymentButton error:', err);
                setTestResults(prev => ({ ...prev, paymentTest: false }));
              }}
            />
          </div>
        </div>

        {/* Console Instructions */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">📋 What to Look For</h3>
          <div className="space-y-2 text-gray-300 text-sm">
            <p><strong>In Browser Console (F12):</strong></p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>✅ Look for: <code className="bg-gray-900 px-2 py-1 rounded">"🔒 Using V3 payment processor"</code></li>
              <li>✅ Look for: <code className="bg-gray-900 px-2 py-1 rounded">"🔄 Processing V3 payment"</code></li>
              <li>✅ Look for: <code className="bg-gray-900 px-2 py-1 rounded">"✅ Payment successful!"</code></li>
            </ul>
            <p className="mt-4"><strong>On the Page:</strong></p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>✅ Look for badge: <code className="bg-gray-900 px-2 py-1 rounded">"🔒 Using V3 (Secure)"</code></li>
            </ul>
            <p className="mt-4"><strong>After Payment:</strong></p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>✅ Transaction signature in console</li>
              <li>✅ Click explorer link to verify on Solana Explorer</li>
              <li>✅ Check Program ID matches V3: <code className="bg-gray-900 px-2 py-1 rounded">ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb</code></li>
            </ul>
          </div>
        </div>

        {/* Payment Test Result */}
        {testResults.paymentTest !== null && (
          <div className={`mt-8 rounded-lg p-6 border ${
            testResults.paymentTest
              ? 'bg-green-900/20 border-green-500'
              : 'bg-red-900/20 border-red-500'
          }`}>
            <div className="flex items-center gap-3">
              {testResults.paymentTest ? (
                <>
                  <CheckCircle className="h-6 w-6 text-green-500" />
                  <h3 className="text-xl font-bold text-green-400">Payment Test: Success!</h3>
                </>
              ) : (
                <>
                  <XCircle className="h-6 w-6 text-red-500" />
                  <h3 className="text-xl font-bold text-red-400">Payment Test: Failed</h3>
                </>
              )}
            </div>
            <p className="text-gray-300 mt-2">
              {testResults.paymentTest
                ? 'V3 payment was processed successfully! Check console for transaction details.'
                : 'Payment failed. Check console for error details.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

