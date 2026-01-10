import { proxyRequest } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  
  // Get the backend URL from runtime configuration. 
  // In Docker, this will be 'http://backend:8000'.
  const backendBaseUrl = config.public.apiBaseUrl

  // Reconstruct the target URL. 
  // event.path will be the full path requested by the client, e.g., '/api/v1/receipts'
  const targetUrl = `${backendBaseUrl}${event.path}`

  console.log(`[Server Proxy] Forwarding request to: ${targetUrl}`)

  // Use the built-in proxyRequest function to forward the request.
  // This handles methods, headers, body, etc., automatically.
  return proxyRequest(event, targetUrl, {
    // By not providing a custom `fetch` instance, we use the default global fetch,
    // which is more robust for this proxying scenario.
  })
})
