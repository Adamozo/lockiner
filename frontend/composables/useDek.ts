/**
 * useDek — Data Encryption Key composable
 *
 * All crypto ops use the Web Crypto API (browser only).
 * The server never sees plain DEK or KEK.
 *
 * Flow:
 *   registration : generateDek → deriveKek(password, salt) → encryptDek → exportDekAsHex (recovery key)
 *   login        : deriveKek(password, dek_salt) → decryptDek → storeDekInSession
 *   change-pw    : getDekFromSession → deriveKek(newPw, newSalt) → encryptDek → send to API
 *   recovery     : importDekFromHex → deriveKek(newPw, newSalt) → encryptDek → send to API
 */

const DEK_SESSION_KEY = 'scrooge_dek'

const hexToBytes = (hex: string): Uint8Array => {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16)
  }
  return bytes
}

const bytesToHex = (bytes: Uint8Array): string =>
  Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')

export const useDek = () => {
  /** Generate a fresh random AES-GCM 256-bit DEK. */
  const generateDek = (): Promise<CryptoKey> =>
    crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt'])

  /** Generate a random 16-byte salt, returned as lowercase hex. */
  const generateSalt = (): string =>
    bytesToHex(crypto.getRandomValues(new Uint8Array(16)))

  /** Derive KEK from password + hex salt via PBKDF2-SHA256 (100 000 iterations). */
  const deriveKek = async (password: string, saltHex: string): Promise<CryptoKey> => {
    const passwordKey = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(password),
      'PBKDF2',
      false,
      ['deriveKey'],
    )
    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: hexToBytes(saltHex),
        iterations: 100_000,
        hash: 'SHA-256',
      },
      passwordKey,
      { name: 'AES-GCM', length: 256 },
      false,
      ['wrapKey', 'unwrapKey'],
    )
  }

  /**
   * Encrypt DEK with KEK using AES-GCM.
   * Returns base64(iv[12] || ciphertext).
   */
  const encryptDek = async (dek: CryptoKey, kek: CryptoKey): Promise<string> => {
    const iv = crypto.getRandomValues(new Uint8Array(12))
    const wrapped = await crypto.subtle.wrapKey('raw', dek, kek, { name: 'AES-GCM', iv })
    const combined = new Uint8Array(iv.length + wrapped.byteLength)
    combined.set(iv)
    combined.set(new Uint8Array(wrapped), iv.length)
    return btoa(String.fromCharCode(...combined))
  }

  /**
   * Decrypt encrypted DEK (base64) with KEK.
   * Returns a CryptoKey usable for encrypt/decrypt.
   */
  const decryptDek = async (encryptedDekB64: string, kek: CryptoKey): Promise<CryptoKey> => {
    const combined = Uint8Array.from(atob(encryptedDekB64), c => c.charCodeAt(0))
    const iv = combined.slice(0, 12)
    const wrapped = combined.slice(12)
    return crypto.subtle.unwrapKey(
      'raw',
      wrapped,
      kek,
      { name: 'AES-GCM', iv },
      { name: 'AES-GCM', length: 256 },
      true,
      ['encrypt', 'decrypt'],
    )
  }

  /** Export DEK as hex string (shown to user as recovery key). */
  const exportDekAsHex = async (dek: CryptoKey): Promise<string> => {
    const raw = await crypto.subtle.exportKey('raw', dek)
    return bytesToHex(new Uint8Array(raw))
  }

  /** Import DEK from hex recovery key. */
  const importDekFromHex = (hex: string): Promise<CryptoKey> =>
    crypto.subtle.importKey(
      'raw',
      hexToBytes(hex),
      { name: 'AES-GCM', length: 256 },
      true,
      ['encrypt', 'decrypt'],
    )

  /** Persist DEK in sessionStorage (hex-encoded). Client-only. */
  const storeDekInSession = async (dek: CryptoKey): Promise<void> => {
    if (import.meta.client) {
      const hex = await exportDekAsHex(dek)
      sessionStorage.setItem(DEK_SESSION_KEY, hex)
    }
  }

  /** Retrieve DEK from sessionStorage. Returns null if missing or on server. */
  const getDekFromSession = async (): Promise<CryptoKey | null> => {
    if (!import.meta.client) return null
    const hex = sessionStorage.getItem(DEK_SESSION_KEY)
    if (!hex) return null
    try {
      return await importDekFromHex(hex)
    } catch {
      return null
    }
  }

  /** Remove DEK from sessionStorage on logout. */
  const clearDekFromSession = (): void => {
    if (import.meta.client) {
      sessionStorage.removeItem(DEK_SESSION_KEY)
    }
  }

  return {
    generateDek,
    generateSalt,
    deriveKek,
    encryptDek,
    decryptDek,
    exportDekAsHex,
    importDekFromHex,
    storeDekInSession,
    getDekFromSession,
    clearDekFromSession,
  }
}
