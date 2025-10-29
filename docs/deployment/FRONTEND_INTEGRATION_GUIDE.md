# 🎨 Frontend Integration Guide

**React/Next.js components for all three phases**

---

## 📊 Overview

This guide shows how to build frontend UI for:
1. **Phase 1:** Context insights and pattern visualization
2. **Phase 2:** Token dashboard, staking interface
3. **Phase 3:** Team management, chat, collaboration

---

## 🚀 Quick Setup

### **1. Install Dependencies**

```bash
cd frontend
npm install axios @tanstack/react-query zustand
```

### **2. Create API Client**

```typescript
// frontend/src/lib/api-client.ts

import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

---

## 📦 Phase 1: Context Insights Component

```typescript
// frontend/src/components/ContextInsights.tsx

import React, { useState } from 'react';
import apiClient from '@/lib/api-client';

interface Pattern {
  pattern_type: string;
  description: string;
  confidence: number;
}

interface ContextInsightsProps {
  userId: int;
  currentMessage: string;
}

export const ContextInsights: React.FC<ContextInsightsProps> = ({
  userId,
  currentMessage
}) => {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/context/insights', {
        user_id: userId,
        current_message: currentMessage
      });
      setInsights(response.data);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">AI Context Insights</h2>
      
      <button
        onClick={fetchInsights}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Analyzing...' : 'Analyze Message'}
      </button>

      {insights && (
        <div className="mt-6 space-y-4">
          {/* Risk Assessment */}
          <div className="p-4 border rounded">
            <h3 className="font-semibold mb-2">Risk Assessment</h3>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                insights.risk_assessment.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                insights.risk_assessment.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {insights.risk_assessment.risk_level.toUpperCase()}
              </span>
              <span className="text-sm text-gray-600">
                Confidence: {(insights.risk_assessment.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Detected Patterns */}
          {insights.detected_patterns.length > 0 && (
            <div className="p-4 border rounded">
              <h3 className="font-semibold mb-2">Detected Patterns</h3>
              <div className="space-y-2">
                {insights.detected_patterns.map((pattern: Pattern, idx: number) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {pattern.pattern_type}
                    </span>
                    <span className="text-gray-700">{pattern.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Similar Attacks */}
          {insights.similar_attacks.length > 0 && (
            <div className="p-4 border rounded">
              <h3 className="font-semibold mb-2">Similar Historical Attacks</h3>
              <p className="text-sm text-gray-600">
                Found {insights.similar_attacks.length} similar attempts
              </p>
            </div>
          )}

          {/* Token Usage */}
          <div className="text-xs text-gray-500">
            Context tokens used: ~{insights.token_usage}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 💰 Phase 2: Token Dashboard

```typescript
// frontend/src/components/TokenDashboard.tsx

import React, { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

interface TokenMetrics {
  token_balance: float;
  discount_rate: float;
  tokens_to_next_tier: float;
}

interface StakingPosition {
  position_id: int;
  staked_amount: float;
  lock_period_days: int;
  unlocks_at: string;
  estimated_monthly_rewards: float;
}

export const TokenDashboard: React.FC<{ userId: int; walletAddress: string }> = ({
  userId,
  walletAddress
}) => {
  const [metrics, setMetrics] = useState<TokenMetrics | null>(null);
  const [positions, setPositions] = useState<StakingPosition[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTokenData();
  }, [userId, walletAddress]);

  const fetchTokenData = async () => {
    try {
      // Fetch balance
      const balanceResponse = await apiClient.post('/api/token/balance/check', {
        wallet_address: walletAddress,
        user_id: userId
      });
      setMetrics(balanceResponse.data);

      // Fetch staking positions
      const stakingResponse = await apiClient.get(`/api/token/staking/user/${userId}`);
      setPositions(stakingResponse.data.positions);
    } catch (error) {
      console.error('Failed to fetch token data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading token data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Token Balance */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-2">Your $100Bs Balance</h2>
        <div className="text-4xl font-bold mb-4">
          {metrics?.token_balance.toLocaleString() || '0'}
        </div>
        <div className="flex items-center gap-4">
          <div className="px-3 py-1 bg-white bg-opacity-20 rounded">
            {(metrics?.discount_rate * 100 || 0)}% discount
          </div>
          {metrics && metrics.tokens_to_next_tier > 0 && (
            <div className="text-sm">
              {metrics.tokens_to_next_tier.toLocaleString()} more for next tier
            </div>
          )}
        </div>
      </div>

      {/* Staking Positions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold mb-4">Staking Positions</h3>
        
        {positions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No active staking positions
            <button className="block mt-4 mx-auto px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Start Staking
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {positions.map((position) => (
              <div key={position.position_id} className="border rounded p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold">
                      {position.staked_amount.toLocaleString()} $100Bs
                    </div>
                    <div className="text-sm text-gray-600">
                      {position.lock_period_days} days
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-green-600 font-semibold">
                      ${position.estimated_monthly_rewards.toFixed(2)}/month
                    </div>
                    <div className="text-xs text-gray-500">
                      Unlocks {new Date(position.unlocks_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Discount Tiers Info */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="font-semibold mb-3">Discount Tiers</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>1,000,000+ tokens</span>
            <span className="text-green-600 font-medium">10% off</span>
          </div>
          <div className="flex justify-between">
            <span>10,000,000+ tokens</span>
            <span className="text-green-600 font-medium">25% off</span>
          </div>
          <div className="flex justify-between">
            <span>100,000,000+ tokens</span>
            <span className="text-green-600 font-medium">50% off</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## 👥 Phase 3: Team Dashboard

```typescript
// frontend/src/components/TeamDashboard.tsx

import React, { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

interface Team {
  id: int;
  name: string;
  description: string;
  total_pool: float;
  member_count: int;
  invite_code: string;
}

interface TeamMember {
  user_id: int;
  display_name: string;
  total_contributed: float;
  contribution_percentage: float;
}

export const TeamDashboard: React.FC<{ teamId: int; userId: int }> = ({
  teamId,
  userId
}) => {
  const [team, setTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeamData();
  }, [teamId]);

  const fetchTeamData = async () => {
    try {
      // Fetch team details
      const teamResponse = await apiClient.get(`/api/teams/${teamId}`);
      setTeam(teamResponse.data);

      // Fetch members
      const membersResponse = await apiClient.get(`/api/teams/${teamId}/members`);
      setMembers(membersResponse.data.members);
    } catch (error) {
      console.error('Failed to fetch team data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContribute = async (amount: float) => {
    try {
      await apiClient.post(`/api/teams/${teamId}/contribute`, {
        user_id: userId,
        amount
      });
      fetchTeamData(); // Refresh
    } catch (error) {
      console.error('Failed to contribute:', error);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading team data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Team Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">{team?.name}</h1>
            <p className="text-gray-600 mt-2">{team?.description}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Invite Code</div>
            <div className="text-xl font-mono font-bold">{team?.invite_code}</div>
          </div>
        </div>

        {/* Team Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-blue-50 p-4 rounded">
            <div className="text-sm text-gray-600">Team Pool</div>
            <div className="text-2xl font-bold text-blue-600">
              ${team?.total_pool.toFixed(2)}
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded">
            <div className="text-sm text-gray-600">Members</div>
            <div className="text-2xl font-bold text-green-600">
              {team?.member_count}
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded">
            <div className="text-sm text-gray-600">Attempts</div>
            <div className="text-2xl font-bold text-purple-600">
              {team?.total_attempts || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Members List */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Team Members</h2>
        <div className="space-y-3">
          {members.map((member) => (
            <div key={member.user_id} className="flex justify-between items-center p-3 border rounded">
              <div>
                <div className="font-semibold">{member.display_name}</div>
                <div className="text-sm text-gray-600">
                  Contributed: ${member.total_contributed.toFixed(2)}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">
                  {member.contribution_percentage.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">of pool</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Contribute Button */}
      <button
        onClick={() => {
          const amount = prompt('Enter amount to contribute:');
          if (amount) handleContribute(parseFloat(amount));
        }}
        className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
      >
        Contribute to Team Pool
      </button>
    </div>
  );
};
```

---

## 💬 Phase 3: Team Chat Component

```typescript
// frontend/src/components/TeamChat.tsx

import React, { useState, useEffect, useRef } from 'react';
import apiClient from '@/lib/api-client';

interface Message {
  id: int;
  user_id: int;
  display_name: string;
  content: string;
  message_type: string;
  created_at: string;
}

export const TeamChat: React.FC<{ teamId: int; userId: int }> = ({
  teamId,
  userId
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [teamId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const response = await apiClient.get(`/api/teams/${teamId}/messages`, {
        params: { user_id: userId, limit: 50 }
      });
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      await apiClient.post(`/api/teams/${teamId}/messages`, {
        user_id: userId,
        content: newMessage,
        message_type: 'text'
      });
      setNewMessage('');
      await fetchMessages();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="font-bold">Team Chat</h3>
        <p className="text-sm text-gray-500">Collaborate and share strategies</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.user_id === userId ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.user_id === userId
                  ? 'bg-blue-600 text-white'
                  : message.message_type === 'strategy'
                  ? 'bg-purple-100 text-purple-900'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="text-xs font-semibold mb-1">
                {message.display_name}
              </div>
              <div>{message.content}</div>
              <div className="text-xs opacity-70 mt-1">
                {new Date(message.created_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t flex gap-2">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
};
```

---

## 🎯 State Management (Optional)

Using Zustand for global state:

```typescript
// frontend/src/store/useStore.ts

import { create } from 'zustand';

interface Store {
  userId: int | null;
  walletAddress: string | null;
  tokenBalance: float;
  currentTeamId: int | null;
  
  setUserId: (id: int) => void;
  setWalletAddress: (address: string) => void;
  setTokenBalance: (balance: float) => void;
  setCurrentTeamId: (id: int) => void;
}

export const useStore = create<Store>((set) => ({
  userId: null,
  walletAddress: null,
  tokenBalance: 0,
  currentTeamId: null,
  
  setUserId: (id) => set({ userId: id }),
  setWalletAddress: (address) => set({ walletAddress: address }),
  setTokenBalance: (balance) => set({ tokenBalance: balance }),
  setCurrentTeamId: (id) => set({ currentTeamId: id }),
}));
```

---

## 📦 Complete Page Example

```typescript
// frontend/src/app/dashboard/page.tsx

import React from 'react';
import { ContextInsights } from '@/components/ContextInsights';
import { TokenDashboard } from '@/components/TokenDashboard';
import { TeamDashboard } from '@/components/TeamDashboard';
import { TeamChat } from '@/components/TeamChat';

export default function DashboardPage() {
  const userId = 1; // Get from auth
  const walletAddress = "..."; // Get from wallet
  const teamId = 1; // Get from user's teams

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Phase 2: Token Dashboard */}
        <div>
          <TokenDashboard userId={userId} walletAddress={walletAddress} />
        </div>

        {/* Phase 1: Context Insights */}
        <div>
          <ContextInsights userId={userId} currentMessage="Test message" />
        </div>

        {/* Phase 3: Team Dashboard */}
        <div>
          <TeamDashboard teamId={teamId} userId={userId} />
        </div>

        {/* Phase 3: Team Chat */}
        <div>
          <TeamChat teamId={teamId} userId={userId} />
        </div>
      </div>
    </div>
  );
}
```

---

## 🚀 Next Steps

1. **Customize styling** to match your design system
2. **Add authentication** (JWT tokens)
3. **Implement WebSocket** for real-time chat
4. **Add error handling** and loading states
5. **Optimize performance** with React Query
6. **Add animations** for better UX

---

**Frontend components ready to use! Just add API_URL and start building. 🎨**

