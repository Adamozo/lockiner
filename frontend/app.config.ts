export default defineAppConfig({
  ui: {
    primary: 'cyan',
    gray: 'neutral',

    button: {
      default: {
        size: 'md',
        loadingIcon: 'i-heroicons-arrow-path-20-solid',
      },
      variant: {
        solid: 'shadow-sm hover:shadow-lg transition-all duration-300',
        outline: 'border-2 hover:shadow-lg transition-all duration-300',
        ghost: 'hover:bg-white/5 transition-all duration-300',
      },
      color: {
        primary: {
          solid: 'bg-gradient-to-r from-cyber-blue to-electric-green text-background-black font-semibold hover:shadow-xl hover:shadow-cyber-blue/30 hover:-translate-y-1 border-0',
        },
        error: {
          solid: 'bg-gradient-to-r from-danger-red to-pink-500 text-white font-semibold hover:shadow-xl hover:shadow-danger-red/30 hover:-translate-y-1 border-0',
        },
        neutral: {
          outline: 'border-border-gray bg-transparent text-pure-white hover:border-electric-green hover:shadow-electric-green/20',
        },
      },
    },

    // Card configuration removed - causes modal positioning issues

    badge: {
      rounded: 'rounded-md',
      size: {
        sm: 'text-xs px-2 py-1',
      },
      color: {
        primary: {
          solid: 'bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30 ring-0',
        },
        success: {
          solid: 'bg-electric-green/20 text-electric-green border border-electric-green/30 ring-0',
        },
        error: {
          solid: 'bg-danger-red/20 text-danger-red border border-danger-red/30 ring-0',
        },
        warning: {
          solid: 'bg-warning-orange/20 text-warning-orange border border-warning-orange/30 ring-0',
        },
      },
    },

    input: {
      base: 'transition-all duration-300',
      color: {
        white: {
          outline: 'border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30',
        },
      },
    },

    select: {
      base: 'transition-all duration-300',
      color: {
        white: {
          outline: 'border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30',
        },
      },
    },

    textarea: {
      base: 'transition-all duration-300',
      color: {
        white: {
          outline: 'border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30',
        },
      },
    },
  },
})
