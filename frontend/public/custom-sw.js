// Custom Service Worker fragment for push notifications
// Imported by Workbox via importScripts

self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? { title: 'LockIner', body: 'Nowe powiadomienie' }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/pwa-icons/pwa-192x192.png',
      badge: '/pwa-icons/pwa-64x64.png',
      tag: data.tag || 'lockiner-notification',
      renotify: true,
      data: { url: data.url || '/notifications' },
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const targetUrl = event.notification.data?.url || '/notifications'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (const client of windowClients) {
        if (new URL(client.url).origin === self.location.origin) {
          client.navigate(targetUrl)
          return client.focus()
        }
      }
      return clients.openWindow(targetUrl)
    })
  )
})
