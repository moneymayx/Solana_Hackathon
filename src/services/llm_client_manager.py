"""
LLM Client Manager for Multi-Provider AI Testing
==================================================

Dynamic, environment-based LLM provider manager that auto-discovers available LLMs
from environment variables matching the pattern: *LLM_API_KEY or *API_KEY

Examples:
- ANTHROPIC_LLM_API_KEY → Anthropic Claude
- OPENAI_LLM_API_KEY → OpenAI GPT-4
- COHERE_LLM_API_KEY → Cohere
- etc.

This approach allows easy addition of new LLM providers without code changes.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class UnifiedLLMClient:
    """
    Unified LLM client that can handle multiple providers dynamically
    Auto-detects provider type based on API key and configures accordingly
    """

    @staticmethod
    def _resolve_model_override(provider_name: str, alias: Optional[str] = None) -> Optional[str]:
        """
        Determine the effective model override for a provider based on environment variables.

        The resolution order keeps existing behaviour first (direct {PROVIDER}_MODEL override)
        and then supports alias-style variables such as {PROVIDER}_MODEL_V1 with a selector
        {PROVIDER}_MODEL_ACTIVE=V1, allowing quick swaps without editing the model strings.
        """
        base_key = f"{provider_name.upper()}_MODEL"

        # Preserve legacy behaviour: honour the direct override if present.
        direct_override = os.environ.get(base_key)
        if direct_override and alias is None:
            return direct_override

        if alias:
            alias_key = f"{base_key}_{alias.strip().upper()}"
            alias_override = os.environ.get(alias_key)
            if alias_override:
                return alias_override

        selector_key = f"{base_key}_ACTIVE"
        active_variant = os.environ.get(selector_key)

        if active_variant:
            normalized_variant = active_variant.strip().upper()
            variant_key = f"{base_key}_{normalized_variant}"

            # Use the explicitly versioned/aliased model if defined.
            variant_override = os.environ.get(variant_key)
            if variant_override:
                return variant_override

            # Fall back to treating the selector value as an explicit model name.
            # This keeps the selector usable even if teams prefer to store the model string there directly.
            if active_variant.strip():
                return active_variant.strip()

        return None
    
    # Provider configurations: how to handle each LLM type
    PROVIDER_CONFIGS = {
        'anthropic': {
            'library': 'anthropic',
            'client_init': lambda key: __import__('anthropic').Anthropic(api_key=key),
            'model': 'claude-sonnet-4-20250514',
            'supports_system': True,
            'async': False
        },
        'openai': {
            'library': 'openai',
            'client_init': lambda key: __import__('openai').AsyncOpenAI(api_key=key),
            'model': 'gpt-4',
            'supports_system': True,
            'async': True
        },
        'deepseek': {
            'library': 'openai',  # Uses OpenAI-compatible SDK
            'client_init': lambda key: __import__('openai').AsyncOpenAI(
                api_key=key,
                base_url="https://api.deepseek.com"
            ),
            'model': 'deepseek-chat',
            'supports_system': True,
            'async': True
        },
        'gemini': {
            'library': 'google.generativeai',
            'client_init': None,  # Handled specially in __init__
            'model': 'gemini-pro',
            'supports_system': False,  # Gemini doesn't support separate system prompts
            'async': False
        },
        # Add more providers here as needed
        'cohere': {
            'library': 'cohere',
            'client_init': lambda key: __import__('cohere').AsyncClient(api_key=key),
            'model': 'command-r-plus',
            'supports_system': True,
            'async': True
        },
        'mistral': {
            'library': 'openai',
            'client_init': lambda key: __import__('openai').AsyncOpenAI(
                api_key=key,
                base_url="https://api.mistral.ai/v1"
            ),
            'model': 'mistral-large',
            'supports_system': True,
            'async': True
        },
        'groq': {
            'library': 'openai',
            'client_init': lambda key: __import__('openai').AsyncOpenAI(
                api_key=key,
                base_url="https://api.groq.com/openai/v1"
            ),
            'model': 'llama-3.3-70b-versatile',  # Updated to more capable model
            'supports_system': True,
            'async': True
        },
        'together': {
            'library': 'openai',
            'client_init': lambda key: __import__('openai').AsyncOpenAI(
                api_key=key,
                base_url="https://api.together.xyz/v1"
            ),
            'model': 'meta-llama/Meta-Llama-3-70B-Instruct',
            'supports_system': True,
            'async': True
        }
    }
    
    def __init__(
        self,
        provider_name: str,
        api_key: str,
        model_override: Optional[str] = None,
        alias: Optional[str] = None
    ):
        """
        Initialize client with provider name and API key
        
        Args:
            provider_name: Provider identifier (e.g., 'anthropic', 'openai')
            api_key: API key for the provider
            model_override: Optional explicit model override (for variant clients)
            alias: Optional variant alias (used for logging when multiple models exist)
        """
        self.provider_name = provider_name.lower()
        self.api_key = api_key
        self.variant_alias = alias.lower() if alias else None
        
        if self.provider_name not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Unknown provider: {provider_name}. Supported: {list(self.PROVIDER_CONFIGS.keys())}")
        
        config = self.PROVIDER_CONFIGS[self.provider_name].copy()  # Make a copy to avoid modifying the original
        
        # Check for model overrides (direct or alias-based) in environment variables.
        # This allows ops teams to maintain multiple candidate models and flip between them safely.
        identifier_label = self.provider_name if not self.variant_alias else f"{self.provider_name}:{self.variant_alias}"

        if model_override:
            config['model'] = model_override
            print(f"✅ Using model override for {identifier_label}: {config['model']}")
        else:
            resolved_model = self._resolve_model_override(self.provider_name)
            if resolved_model:
                config['model'] = resolved_model
                print(f"✅ Using model override for {identifier_label}: {config['model']}")
        
        # Initialize client
        try:
            if self.provider_name == 'gemini':
                # Special handling for Gemini
                genai = __import__('google.generativeai', fromlist=[''])
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(config['model'])
            else:
                self.client = config['client_init'](api_key)
            
            self.config = config
            self.available = True
        except ImportError as e:
            print(f"⚠️  {config['library']} not installed for {provider_name}. Install: pip install {config['library']}")
            self.client = None
            self.available = False
    
    async def send_message(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Send a message to the LLM and get a response"""
        if not self.available:
            raise ValueError(f"{self.provider_name} client not available")
        
        conversation_history = conversation_history or []
        
        # Handle different providers
        if self.provider_name == 'anthropic':
            return await self._send_anthropic(system_prompt, user_message, conversation_history)
        elif self.provider_name == 'openai' or self.provider_name in ['deepseek', 'mistral', 'groq', 'together']:
            return await self._send_openai_compatible(system_prompt, user_message, conversation_history)
        elif self.provider_name == 'gemini':
            return await self._send_gemini(system_prompt, user_message, conversation_history)
        elif self.provider_name == 'cohere':
            return await self._send_cohere(system_prompt, user_message, conversation_history)
        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")
    
    async def _send_anthropic(self, system_prompt: str, user_message: str, history: List[Dict[str, str]]):
        """Send message via Anthropic API"""
        messages = history + [{"role": "user", "content": user_message}]
        
        # Anthropic uses sync client
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                model=self.config['model'],
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )
        )
        
        return response.content[0].text
    
    async def _send_openai_compatible(self, system_prompt: str, user_message: str, history: List[Dict[str, str]]):
        """Send message via OpenAI-compatible API (OpenAI, DeepSeek, Mistral, Groq, Together)"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        response = await self.client.chat.completions.create(
            model=self.config['model'],
            max_tokens=1000,
            messages=messages
        )
        
        return response.choices[0].message.content
    
    async def _send_gemini(self, system_prompt: str, user_message: str, history: List[Dict[str, str]]):
        """Send message via Gemini API"""
        # Gemini doesn't have separate system prompts, prepend to message
        full_prompt = f"{system_prompt}\n\n{user_message}"
        
        # Gemini uses sync client
        loop = asyncio.get_event_loop()
        if history:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.start_chat(history=history).send_message(full_prompt)
            )
        else:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(full_prompt)
            )
        
        return response.text
    
    async def _send_cohere(self, system_prompt: str, user_message: str, history: List[Dict[str, str]]):
        """Send message via Cohere API"""
        # Cohere uses different role names
        messages = [{"role": "SYSTEM", "content": system_prompt}]
        messages.extend([{"role": msg.get("role", "USER").upper(), "content": msg.get("content", "")} 
                        for msg in history])
        messages.append({"role": "USER", "content": user_message})
        
        response = await self.client.chat(
            model=self.config['model'],
            messages=messages,
            max_tokens=1000
        )
        
        return response.text
    
    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.provider_name
    
    def get_variant_alias(self) -> Optional[str]:
        """Get the alias for this client variant (None for default)"""
        return self.variant_alias
    
    def is_available(self) -> bool:
        """Check if the client has valid API credentials"""
        return self.available


class LLMClientManager:
    """
    Factory class that auto-discovers available LLM providers from environment variables
    Supports pattern: *LLM_API_KEY or *API_KEY
    """
    
    def __init__(self):
        """Initialize and auto-discover available LLM providers"""
        self.clients: Dict[Tuple[str, Optional[str]], UnifiedLLMClient] = {}
        self._provider_alias_index: Dict[str, List[Optional[str]]] = {}
        self._registered_providers: Set[str] = set()
        self._discover_providers()
    
    def _discover_providers(self):
        """Auto-discover LLM providers from environment variables"""
        all_env_vars = os.environ
        
        # Look for environment variables matching LLM API key patterns
        for env_key in all_env_vars:
            provider_name = None
            
            # Pattern 1: *LLM_API_KEY (e.g., ANTHROPIC_LLM_API_KEY)
            if env_key.endswith('_LLM_API_KEY'):
                provider_name = env_key[:-12].lower()  # Remove '_LLM_API_KEY'
            
            # Pattern 2: *API_KEY for known providers (e.g., OPENAI_API_KEY, GEMINI_API_KEY)
            elif env_key.endswith('_API_KEY'):
                potential_provider = env_key[:-8].lower()  # Remove '_API_KEY'
                # Check if this is a known provider
                if potential_provider in UnifiedLLMClient.PROVIDER_CONFIGS:
                    provider_name = potential_provider
            
            if (
                provider_name
                and provider_name in UnifiedLLMClient.PROVIDER_CONFIGS
                and provider_name not in self._registered_providers
            ):
                api_key = os.getenv(env_key)
                if not api_key:
                    continue
                self._initialize_provider(provider_name, api_key)
    
    def _initialize_provider(self, provider_name: str, api_key: str) -> None:
        """Initialize clients for a provider, including variant aliases when supported"""
        try:
            for alias, client in self._build_clients_for_provider(provider_name, api_key):
                if client.is_available():
                    self._register_client(provider_name, alias, client)
        except Exception as exc:
            print(f"⚠️  Failed to initialize {provider_name}: {exc}")
        finally:
            self._registered_providers.add(provider_name)
    
    def _register_client(
        self,
        provider_name: str,
        alias: Optional[str],
        client: UnifiedLLMClient
    ) -> None:
        """Register a provider client with optional alias"""
        provider_key = provider_name.lower()
        alias_key = alias.lower() if alias else None
        identifier = self._format_identifier(provider_key, alias_key)
        
        self.clients[(provider_key, alias_key)] = client
        alias_list = self._provider_alias_index.setdefault(provider_key, [])
        if alias_key not in alias_list:
            alias_list.append(alias_key)
        
        if alias_key:
            print(f"✅ Discovered LLM: {provider_key.upper()} ({alias_key.upper()})")
        else:
            print(f"✅ Discovered LLM: {provider_key.upper()}")
    
    def _build_clients_for_provider(
        self,
        provider_name: str,
        api_key: str
    ) -> List[Tuple[Optional[str], UnifiedLLMClient]]:
        """Construct default and alias-specific clients for a provider"""
        clients: List[Tuple[Optional[str], UnifiedLLMClient]] = []
        
        # Always include the default client (alias None)
        clients.append((None, UnifiedLLMClient(provider_name, api_key)))
        
        if provider_name.lower() == 'groq':
            alias_models = self._get_model_aliases(provider_name)
            for alias, model_name in alias_models.items():
                try:
                    alias_client = UnifiedLLMClient(
                        provider_name,
                        api_key,
                        model_override=model_name,
                        alias=alias
                    )
                    clients.append((alias, alias_client))
                except Exception as exc:
                    print(f"⚠️  Failed to initialize {provider_name} alias {alias}: {exc}")
        
        return clients
    
    def _get_model_aliases(self, provider_name: str) -> Dict[str, str]:
        """Parse environment variables for provider model aliases"""
        provider_upper = provider_name.upper()
        alias_map: Dict[str, str] = {}
        alias_env_key = f"{provider_upper}_MODEL_ALIASES"
        raw_alias_list = os.environ.get(alias_env_key, "")
        
        alias_candidates: List[str] = [
            alias.strip()
            for alias in raw_alias_list.split(',')
            if alias.strip()
        ]
        
        if not alias_candidates:
            prefix = f"{provider_upper}_MODEL_"
            for env_key, value in os.environ.items():
                if env_key.startswith(prefix):
                    suffix = env_key[len(prefix):]
                    if suffix.upper() in {"ACTIVE", "ALIASES"}:
                        continue
                    if suffix:
                        alias_candidates.append(suffix)
        
        seen_aliases: Set[str] = set()
        for alias in alias_candidates:
            alias_clean = alias.strip()
            if not alias_clean:
                continue
            alias_upper = alias_clean.upper()
            if alias_upper in {"ACTIVE", "ALIASES"} or alias_upper in seen_aliases:
                continue
            model_key = f"{provider_upper}_MODEL_{alias_upper}"
            model_value = os.environ.get(model_key)
            if model_value:
                alias_map[alias_clean.lower()] = model_value.strip()
                seen_aliases.add(alias_upper)
        
        return alias_map
    
    def _format_identifier(self, provider: str, alias: Optional[str]) -> str:
        """Format a unique identifier for provider+alias combos"""
        return provider if alias is None else f"{provider}:{alias}"
    
    def get_client(self, provider: str, alias: Optional[str] = None) -> Optional[UnifiedLLMClient]:
        """
        Get a client by provider name
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'openai' or 'groq:v1')
            alias: Optional alias component (e.g., 'v1')
        
        Returns:
            UnifiedLLMClient instance or None if not available
        """
        provider_key = provider.lower()
        alias_key = alias.lower() if alias else None
        
        if alias is None and ':' in provider_key:
            provider_key, alias_fragment = provider_key.split(':', 1)
            alias_key = alias_fragment or None
        
        return self.clients.get((provider_key, alias_key))
    
    def get_available_clients(self) -> Dict[str, UnifiedLLMClient]:
        """
        Get all available (configured) LLM clients
        
        Returns:
            Dictionary mapping provider names to client instances
        """
        return {
            self._format_identifier(provider, alias): client
            for (provider, alias), client in self.clients.items()
        }
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names
        
        Returns:
            List of provider names with valid API keys
        """
        return [
            self._format_identifier(provider, alias)
            for (provider, alias) in self.clients.keys()
        ]
    
    def get_available_aliases(self, provider: str) -> List[str]:
        """
        Get list of available aliases for a provider (includes 'default' for primary client)
        """
        provider_key = provider.lower()
        aliases = self._provider_alias_index.get(provider_key, [])
        formatted_aliases: List[str] = []
        for alias in aliases:
            if alias is None:
                formatted_aliases.append('default')
            else:
                formatted_aliases.append(alias)
        return formatted_aliases
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a specific provider is available
        
        Args:
            provider: Provider name
        
        Returns:
            True if provider has valid API credentials
        """
        provider_key = provider.lower()
        alias_key: Optional[str] = None
        if ':' in provider_key:
            provider_key, alias_fragment = provider_key.split(':', 1)
            alias_key = alias_fragment or None
        return (provider_key, alias_key) in self.clients
    
    def add_custom_provider(self, provider_name: str, api_key: str, config: Dict):
        """
        Add a custom provider configuration at runtime
        
        Args:
            provider_name: Name of the provider
            api_key: API key for the provider
            config: Configuration dict matching PROVIDER_CONFIGS format
        """
        if provider_name in UnifiedLLMClient.PROVIDER_CONFIGS:
            print(f"⚠️  Provider {provider_name} already exists")
            return
        
        UnifiedLLMClient.PROVIDER_CONFIGS[provider_name] = config
        
        # Try to initialize
        try:
            client = UnifiedLLMClient(provider_name, api_key)
            if client.is_available():
                self._register_client(provider_name, None, client)
                print(f"✅ Added custom LLM: {provider_name.upper()}")
        except Exception as e:
            print(f"⚠️  Failed to add custom provider {provider_name}: {e}")
