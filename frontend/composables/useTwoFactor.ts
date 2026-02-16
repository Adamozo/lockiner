/**
 * Two-factor authentication composable
 * Handles 2FA setup, verification, and management
 */

import type {
  TwoFactorSetupResponse,
  TwoFactorVerifySetupResponse,
  TwoFactorStatusResponse,
  TwoFactorRegenerateResponse,
} from '~/types/api'

export function useTwoFactor() {
  const api = useApi()

  const setup2FA = async (): Promise<TwoFactorSetupResponse> => {
    return await api<TwoFactorSetupResponse>('/api/v1/auth/2fa/setup', {
      method: 'POST',
    })
  }

  const verifySetup = async (code: string): Promise<TwoFactorVerifySetupResponse> => {
    return await api<TwoFactorVerifySetupResponse>('/api/v1/auth/2fa/verify-setup', {
      method: 'POST',
      body: { code },
    })
  }

  const disable2FA = async (code: string): Promise<void> => {
    await api('/api/v1/auth/2fa/disable', {
      method: 'POST',
      body: { code },
    })
  }

  const get2FAStatus = async (): Promise<TwoFactorStatusResponse> => {
    return await api<TwoFactorStatusResponse>('/api/v1/auth/2fa/status')
  }

  const regenerateRecoveryCodes = async (code: string): Promise<TwoFactorRegenerateResponse> => {
    return await api<TwoFactorRegenerateResponse>('/api/v1/auth/2fa/regenerate-recovery', {
      method: 'POST',
      body: { code },
    })
  }

  return {
    setup2FA,
    verifySetup,
    disable2FA,
    get2FAStatus,
    regenerateRecoveryCodes,
  }
}
