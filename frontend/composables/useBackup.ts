/**
 * Backup & Data Export composable
 * Handles personal and household backup settings, scheduling, passwords, and Google Drive integration
 */

export interface BackupSettings {
  id: number
  user_id: number
  password_configured: boolean
  auto_backup_enabled: boolean
  frequency: string // 'daily' | 'weekly' | 'monthly'
  hour: number
  minute: number
  day_of_week: number | null
  day_of_month: number | null
  google_drive_connected: boolean
  google_drive_folder_id: string | null
  last_backup_at: string | null
  last_backup_filename: string | null
  last_backup_size_bytes: number | null
  last_backup_error: string | null
  created_at: string
  updated_at: string | null
}

export interface HouseholdBackupSettings extends BackupSettings {
  household_id: number
  configured_by_user_id: number | null
}

export interface BackupScheduleUpdate {
  auto_backup_enabled: boolean
  frequency: string
  hour: number
  minute: number
  day_of_week?: number | null
  day_of_month?: number | null
}

export function useBackup() {
  const api = useApi()

  // ─── Helper: trigger browser file download from a Blob ───────────────────

  const triggerDownload = (blob: Blob, filename: string): void => {
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    document.body.removeChild(anchor)
    URL.revokeObjectURL(url)
  }

  // ─── Helper: raw fetch with Bearer token ─────────────────────────────────

  const rawFetchWithAuth = async (path: string): Promise<Response> => {
    const tokenCookie = useCookie<string | null>('scrooge_access_token')
    const token = tokenCookie.value

    const headers: HeadersInit = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    return fetch(path, { headers })
  }

  // ─── User backup ─────────────────────────────────────────────────────────

  /**
   * Get user backup settings
   */
  const getSettings = async (): Promise<BackupSettings> => {
    return await api<BackupSettings>('/api/v1/backup/settings')
  }

  /**
   * Update auto-backup schedule settings
   */
  const updateSchedule = async (data: BackupScheduleUpdate): Promise<BackupSettings> => {
    return await api<BackupSettings>('/api/v1/backup/settings/schedule', {
      method: 'PUT',
      body: data,
    })
  }

  /**
   * Get configured backup password status (and value if set)
   */
  const getPassword = async (): Promise<{ password: string | null; configured: boolean }> => {
    return await api<{ password: string | null; configured: boolean }>('/api/v1/backup/password')
  }

  /**
   * Set or update the backup encryption password
   */
  const setPassword = async (password: string): Promise<void> => {
    await api('/api/v1/backup/password', {
      method: 'PUT',
      body: { password },
    })
  }

  /**
   * Download personal backup as an encrypted ZIP file
   */
  const downloadBackup = async (): Promise<void> => {
    const response = await rawFetchWithAuth('/api/v1/backup/download')

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`)
    }

    const blob = await response.blob()

    // Try to get filename from Content-Disposition header
    const disposition = response.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename[^;=\n]*=(['"]?)([^'";\n]+)\1/)
    const filename = match ? match[2] : 'backup.zip'

    triggerDownload(blob, filename)
  }

  /**
   * Get the OAuth URL to connect Google Drive
   */
  const getGoogleDriveAuthUrl = async (): Promise<string> => {
    const response = await api<{ auth_url: string }>('/api/v1/backup/google-drive/auth-url')
    return response.auth_url
  }

  /**
   * Disconnect Google Drive integration
   */
  const disconnectGoogleDrive = async (): Promise<void> => {
    await api('/api/v1/backup/google-drive/disconnect', {
      method: 'DELETE',
    })
  }

  // ─── Household backup ────────────────────────────────────────────────────

  /**
   * Get household backup settings
   */
  const getHouseholdSettings = async (householdId: number): Promise<HouseholdBackupSettings> => {
    return await api<HouseholdBackupSettings>(`/api/v1/backup/household/${householdId}/settings`)
  }

  /**
   * Update household auto-backup schedule settings
   */
  const updateHouseholdSchedule = async (
    householdId: number,
    data: BackupScheduleUpdate,
  ): Promise<HouseholdBackupSettings> => {
    return await api<HouseholdBackupSettings>(
      `/api/v1/backup/household/${householdId}/settings/schedule`,
      {
        method: 'PUT',
        body: data,
      },
    )
  }

  /**
   * Get household backup password status
   */
  const getHouseholdPassword = async (
    householdId: number,
  ): Promise<{ password: string | null; configured: boolean }> => {
    return await api<{ password: string | null; configured: boolean }>(
      `/api/v1/backup/household/${householdId}/password`,
    )
  }

  /**
   * Set or update the household backup encryption password
   */
  const setHouseholdPassword = async (householdId: number, password: string): Promise<void> => {
    await api(`/api/v1/backup/household/${householdId}/password`, {
      method: 'PUT',
      body: { password },
    })
  }

  /**
   * Download household backup as an encrypted ZIP file
   */
  const downloadHouseholdBackup = async (householdId: number): Promise<void> => {
    const response = await rawFetchWithAuth(
      `/api/v1/backup/household/${householdId}/download`,
    )

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`)
    }

    const blob = await response.blob()

    const disposition = response.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename[^;=\n]*=(['"]?)([^'";\n]+)\1/)
    const filename = match ? match[2] : `household_${householdId}_backup.zip`

    triggerDownload(blob, filename)
  }

  /**
   * Get the OAuth URL to connect Google Drive for a household
   */
  const getHouseholdGoogleDriveAuthUrl = async (householdId: number): Promise<string> => {
    const response = await api<{ auth_url: string }>(
      `/api/v1/backup/household/${householdId}/google-drive/auth-url`,
    )
    return response.auth_url
  }

  /**
   * Disconnect Google Drive integration for a household
   */
  const disconnectHouseholdGoogleDrive = async (householdId: number): Promise<void> => {
    await api(`/api/v1/backup/household/${householdId}/google-drive/disconnect`, {
      method: 'DELETE',
    })
  }

  return {
    // User backup
    getSettings,
    updateSchedule,
    getPassword,
    setPassword,
    downloadBackup,
    getGoogleDriveAuthUrl,
    disconnectGoogleDrive,

    // Household backup
    getHouseholdSettings,
    updateHouseholdSchedule,
    getHouseholdPassword,
    setHouseholdPassword,
    downloadHouseholdBackup,
    getHouseholdGoogleDriveAuthUrl,
    disconnectHouseholdGoogleDrive,
  }
}
