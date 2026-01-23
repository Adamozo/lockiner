// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@unocss/nuxt',
    '@nuxt/ui',
    '@pinia/nuxt',
  ],

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
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/favicon.svg' },
      ],
    },
  },
})
