// UnoCSS configuration for LockIner
// Cyber-themed design system from MakeItRemote

export default {
  theme: {
    colors: {
      // Cyber theme colors from MakeItRemote
      'pure-white': '#FFFFFF',
      'cyber-blue': '#00D4FF',
      'electric-green': '#00FF88',
      'background-black': '#0A0A0A',
      'card-black': '#1A1A1A',
      'border-gray': '#333333',
      'danger-red': '#FF3366',
      'warning-orange': '#FFA500',
    },
    borderRadius: {
      '8': '8px',
      '12': '12px',
      '16': '16px',
      '20': '20px',
    },
    boxShadow: {
      'glow-cyan': '0 0 20px rgba(0, 212, 255, 0.3)',
      'glow-green': '0 0 20px rgba(0, 255, 136, 0.3)',
      'glow-red': '0 0 20px rgba(255, 51, 102, 0.3)',
    },
  },

  rules: [
    // Gradient backgrounds
    ['gradient-brand', { background: 'linear-gradient(135deg, #00D4FF, #00FF88)' }],
    ['gradient-danger', { background: 'linear-gradient(135deg, #FF3366, #FF6B9D)' }],
    ['gradient-radial-green', { background: 'radial-gradient(circle, rgba(0,255,136,0.2) 0%, transparent 70%)' }],
    ['gradient-radial-blue', { background: 'radial-gradient(circle, rgba(0,212,255,0.2) 0%, transparent 70%)' }],

    // Glassmorphism
    ['backdrop-blur-glass', { 'backdrop-filter': 'blur(20px)', '-webkit-backdrop-filter': 'blur(20px)' }],

    // Glass effect utility
    ['glass', {
      background: 'rgba(26, 26, 26, 0.8)',
      'backdrop-filter': 'blur(20px)',
      '-webkit-backdrop-filter': 'blur(20px)',
    }],
  ],

  shortcuts: [
    // Card utilities
    {
      'card-glass': 'bg-card-black/80 backdrop-blur-glass border border-border-gray',
      'card-hover-lift': 'transition-all duration-300 hover:transform hover:-translate-y-2 hover:shadow-xl',
      'card-base': 'bg-card-black border border-border-gray rounded-lg',
    },

    // Button utilities
    {
      'btn-base': 'px-6 py-3 rounded-lg font-600 text-base transition-all duration-300',
      'btn-lift-hover': 'hover:transform hover:-translate-y-1',
    },

    // Text utilities
    {
      'text-gradient-brand': 'bg-gradient-to-r from-cyber-blue to-electric-green bg-clip-text text-transparent',
      'text-muted': 'text-pure-white/80',
      'text-subtle': 'text-pure-white/70',
      'text-faint': 'text-pure-white/60',
    },

    // Responsive spacing
    {
      'section-responsive': 'py-16 px-4 md:py-32 md:px-8',
      'container-responsive': 'max-w-1200px mx-auto px-4 md:px-8',
    },
  ],

  content: {
    pipeline: {
      include: [
        /\.(vue|svelte|[jt]sx|mdx?|astro|elm|php|phtml|html)($|\?)/,
        'components/**/*.{vue,js,ts}',
        'layouts/**/*.vue',
        'pages/**/*.vue',
        'composables/**/*.{js,ts}',
        'plugins/**/*.{js,ts}',
        'App.{js,ts,vue}',
        'app.{js,ts,vue}',
        'Error.{js,ts,vue}',
        'error.{js,ts,vue}',
        'app.config.{js,ts}',
      ],
    },
  },
}
