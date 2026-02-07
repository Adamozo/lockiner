// Custom Service Worker fragment for push notifications
// Imported by Workbox via importScripts

self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? { title: 'LockIner', body: 'Nowe powiadomienie' }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/pwa-icons/pwa-192x192.png',
      badge: '/pwa-icons/pwa-64x64.png',
      data: { url: '/notifications' },
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/notifications')
  )
})
