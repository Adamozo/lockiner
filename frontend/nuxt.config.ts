// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@unocss/nuxt',
    '@nuxt/ui',
    '@pinia/nuxt',
    '@vite-pwa/nuxt',
    '@nuxtjs/i18n',
  ],

  i18n: {
    defaultLocale: 'en',
    strategy: 'no_prefix',
    restructureDir: false,
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'scrooge_language',
      redirectOn: 'root',
      alwaysRedirect: false,
    },
    locales: [
      { code: 'en', name: 'English', file: 'en.json' },
      { code: 'pl', name: 'Polski', file: 'pl.json' },
    ],
    lazy: true,
    langDir: 'locales/',
  },

  // Icon configuration - bundle icons at build time for production
  icon: {
    serverBundle: 'local',
    clientBundle: {
      scan: true,
    },
  },

  css: [
    '~/assets/css/global.css',
  ],

  // TypeScript configuration
  typescript: {
    strict: true,
    typeCheck: false, // Disabled in dev to avoid vue-tsc watch mode issues
    shim: false, // Disable .vue shims to prevent vue-tsc from running
  },

  // Runtime configuration
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    },
  },

  // Nitro server configuration (for API proxy)
  nitro: {
    // devProxy has been removed in favor of a server-side proxy route
  },

  // UnoCSS configuration
  unocss: {
    preflight: true,
    uno: true,
    attributify: true,
    icons: true,
  },

  // Nuxt UI configuration
  ui: {
    // Configuration is handled in app.config.ts
  },

  // PWA configuration
  pwa: {
    registerType: 'autoUpdate',
    includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
    manifest: {
      name: 'LockIner - Lock In and Improve',
      short_name: 'LockIner',
      description: 'AI-powered personal finance management with receipt OCR',
      theme_color: '#0A0A0A',
      background_color: '#0A0A0A',
      display: 'standalone',
      start_url: '/',
      icons: [
        { src: 'pwa-icons/pwa-64x64.png', sizes: '64x64', type: 'image/png' },
        { src: 'pwa-icons/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: 'pwa-icons/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: 'pwa-icons/maskable-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
        { src: 'pwa-icons/maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff,woff2}'],
      importScripts: ['/custom-sw.js'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-cache',
            expiration: { maxEntries: 10, maxAgeSeconds: 31536000 },
          },
        },
        {
          urlPattern: ({ url }: { url: URL }) => url.pathname.startsWith('/api/'),
          handler: 'NetworkFirst',
          options: {
            cacheName: 'api-cache',
            networkTimeoutSeconds: 10,
            expiration: { maxEntries: 100, maxAgeSeconds: 86400 },
          },
        },
        {
          urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'images-cache',
            expiration: { maxEntries: 100, maxAgeSeconds: 2592000 },
          },
        },
      ],
    },
    devOptions: {
      enabled: false,
      type: 'module',
    },
  },

  // Development server
  devServer: {
    host: '0.0.0.0',
    port: 3000,
  },

  // App configuration
  app: {
    head: {
      title: 'LockIner - Lock In and Improve',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-powered personal finance management with receipt OCR' },
        { name: 'theme-color', content: '#0A0A0A' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: 'LockIner' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
      ],
    },
  },
})
