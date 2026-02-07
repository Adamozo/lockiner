/**
 * Settings management composable
 * Handles API provider configuration for OCR (Gemini, Claude, OpenAI)
 */

export interface APIProviderConfig {
  provider: string
  key_preview: string
  is_active: boolean
  configured_at: string | null
}

export interface APIProviderListResponse {
  providers: APIProviderConfig[]
  active_provider: string | null
}

export interface APIProviderConfigRequest {
  provider: string
  api_key: string
  is_active: boolean
}

// Global state for key configuration
const keyConfigured = ref(false)

export function useSettings() {
  const api = useApi()

  /**
   * Check if Gemini API key is configured
   */
  const getGeminiKeyStatus = async (): Promise<void> => {
    try {
      const response = await api<APIProviderListResponse>('/api/v1/settings/api-providers')
      // Check if there's an active provider configured
      keyConfigured.value = response.active_provider !== null && response.providers.length > 0
    } catch (error) {
      console.error('Failed to check API key status:', error)
      keyConfigured.value = false
    }
  }

  /**
   * Get list of all configured API providers
   */
  const getAPIProviders = async (): Promise<APIProviderListResponse> => {
    try {
      const response = await api<APIProviderListResponse>('/api/v1/settings/api-providers')
      // Update keyConfigured state
      keyConfigured.value = response.active_provider !== null && response.providers.length > 0
      return response
    } catch (error) {
      console.error('Failed to fetch API providers:', error)
      throw error
    }
  }

  /**
   * Add or update API provider configuration
   */
  const addAPIProvider = async (config: APIProviderConfigRequest): Promise<APIProviderConfig> => {
    try {
      const response = await api<APIProviderConfig>('/api/v1/settings/api-providers', {
        method: 'POST',
        body: config,
      })
      return response
    } catch (error) {
      console.error('Failed to add API provider:', error)
      throw error
    }
  }

  /**
   * Set active API provider
   */
  const setActiveProvider = async (provider: string): Promise<void> => {
    try {
      await api('/api/v1/settings/active-provider', {
        method: 'POST',
        body: { provider },
      })
    } catch (error) {
      console.error('Failed to set active provider:', error)
      throw error
    }
  }

  /**
   * Delete API provider configuration
   */
  const deleteAPIProvider = async (provider: string): Promise<void> => {
    try {
      await api(`/api/v1/settings/api-providers/${provider}`, {
        method: 'DELETE',
      })
    } catch (error) {
      console.error('Failed to delete API provider:', error)
      throw error
    }
  }

  return {
    keyConfigured,
    getGeminiKeyStatus,
    getAPIProviders,
    addAPIProvider,
    setActiveProvider,
    deleteAPIProvider,
  }
}
