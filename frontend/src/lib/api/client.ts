const DEFAULT_BACKEND_URL = 'http://localhost:8000'

/**
 * Resolve the backend base URL once so all requests use the same origin.
 * We trim trailing slashes to prevent duplicated separators when joining paths.
 */
export function getBackendUrl(): string {
  const rawUrl = process.env.NEXT_PUBLIC_API_URL || DEFAULT_BACKEND_URL
  return rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl
}

/**
 * Thin wrapper around fetch that automatically prefixes the configured backend URL.
 * Keeping this logic here ensures both web and native surfaces point at the same API host.
 */
export async function backendFetch<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const baseUrl = getBackendUrl()
  const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`

  console.log('🔍 [API] Fetching:', {
    endpoint,
    baseUrl,
    fullUrl: url,
    method: init?.method || 'GET',
    timestamp: new Date().toISOString()
  })

  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    })

    console.log('📡 [API] Response received:', {
      url,
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
      headers: Object.fromEntries(response.headers.entries())
    })

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({})) as { detail?: string; error?: string }
      const message = errorBody.detail || errorBody.error || `Request failed with status ${response.status}`
      console.error('❌ [API] Request failed:', {
        url,
        status: response.status,
        errorBody,
        message
      })
      throw new Error(message)
    }

    const data = await response.json() as T
    console.log('✅ [API] Success:', {
      url,
      dataKeys: typeof data === 'object' && data !== null ? Object.keys(data) : 'non-object',
      dataPreview: typeof data === 'object' && data !== null 
        ? JSON.stringify(data).substring(0, 200) + '...'
        : data
    })
    
    return data
  } catch (error) {
    console.error('💥 [API] Exception caught:', {
      url,
      error: error instanceof Error ? {
        name: error.name,
        message: error.message,
        stack: error.stack
      } : error
    })
    throw error
  }
}

