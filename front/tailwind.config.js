module.exports = {
  content: ['./src/**/*.{html,js,svelte}'],
  theme: {
    extend: {
      colors: {
        // Primary Color (Cambridge Blue)
        'primary': {
          DEFAULT: '#84a59d',
          '100': '#192220',
          '200': '#324440',
          '300': '#4b665f',
          '400': '#65887f',
          '500': '#84a59d',
          '600': '#9cb6b0',
          '700': '#b5c8c4',
          '800': '#cedbd7',
          '900': '#e6edeb'
        },
        // Secondary Color (Hunyadi Yellow)
        'secondary': {
          DEFAULT: '#f6bd60',
          '100': '#412904',
          '200': '#815308',
          '300': '#c27c0b',
          '400': '#f2a11f',
          '500': '#f6bd60',
          '600': '#f8ca80',
          '700': '#f9d7a0',
          '800': '#fbe4bf',
          '900': '#fdf2df'
        },
        // Accent Color (Tea Rose)
        'accent': {
          DEFAULT: '#f5cac3',
          '100': '#4b150d',
          '200': '#962a19',
          '300': '#db432c',
          '400': '#e88677',
          '500': '#f5cac3',
          '600': '#f7d4ce',
          '700': '#f9deda',
          '800': '#fbe9e7',
          '900': '#fdf4f3'
        },
        // Danger Color (Light Coral)
        'danger': {
          DEFAULT: '#f28482',
          '100': '#430807',
          '200': '#87100e',
          '300': '#ca1815',
          '400': '#eb423f',
          '500': '#f28482',
          '600': '#f59d9b',
          '700': '#f7b5b4',
          '800': '#facecd',
          '900': '#fce6e6'
        },
        // Background Color (Linen)
        'background': {
          DEFAULT: '#f7ede2',
          '100': '#4a3014',
          '200': '#956129',
          '300': '#cf904e',
          '400': '#e3bf99',
          '500': '#f7ede2',
          '600': '#f9f1e9',
          '700': '#faf4ee',
          '800': '#fcf8f4',
          '900': '#fdfbf9'
        },
        
        // Keep original names for backward compatibility
        'cambridge': {
          DEFAULT: '#84a59d',
          '100': '#192220',
          '200': '#324440',
          '300': '#4b665f',
          '400': '#65887f',
          '500': '#84a59d',
          '600': '#9cb6b0',
          '700': '#b5c8c4',
          '800': '#cedbd7',
          '900': '#e6edeb'
        },
        'hunyadi': {
          DEFAULT: '#f6bd60',
          '100': '#412904',
          '200': '#815308',
          '300': '#c27c0b',
          '400': '#f2a11f',
          '500': '#f6bd60',
          '600': '#f8ca80',
          '700': '#f9d7a0',
          '800': '#fbe4bf',
          '900': '#fdf2df'
        },
        'tea-rose': {
          DEFAULT: '#f5cac3',
          '100': '#4b150d',
          '200': '#962a19',
          '300': '#db432c',
          '400': '#e88677',
          '500': '#f5cac3',
          '600': '#f7d4ce',
          '700': '#f9deda',
          '800': '#fbe9e7',
          '900': '#fdf4f3'
        },
        'linen': {
          DEFAULT: '#f7ede2',
          '100': '#4a3014',
          '200': '#956129',
          '300': '#cf904e',
          '400': '#e3bf99',
          '500': '#f7ede2',
          '600': '#f9f1e9',
          '700': '#faf4ee',
          '800': '#fcf8f4',
          '900': '#fdfbf9'
        },
        'coral': {
          DEFAULT: '#f28482',
          '100': '#430807',
          '200': '#87100e',
          '300': '#ca1815',
          '400': '#eb423f',
          '500': '#f28482',
          '600': '#f59d9b',
          '700': '#f7b5b4',
          '800': '#facecd',
          '900': '#fce6e6'
        }
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(25, 34, 32, 0.05)',
        'md': '0 4px 6px -1px rgba(25, 34, 32, 0.1), 0 2px 4px -1px rgba(25, 34, 32, 0.06)',
        'lg': '0 10px 15px -3px rgba(25, 34, 32, 0.1), 0 4px 6px -2px rgba(25, 34, 32, 0.05)',
        'xl': '0 20px 25px -5px rgba(25, 34, 32, 0.1), 0 10px 10px -5px rgba(25, 34, 32, 0.04)',
        'inner-sm': 'inset 0 1px 2px 0 rgba(25, 34, 32, 0.05)',
        'inner-md': 'inset 0 2px 4px 0 rgba(25, 34, 32, 0.1)',
        'glow-primary': '0 0 5px rgba(132, 165, 157, 0.5), 0 0 20px rgba(132, 165, 157, 0.3)',
        'glow-secondary': '0 0 5px rgba(246, 189, 96, 0.5), 0 0 20px rgba(246, 189, 96, 0.3)',
        'glow-danger': '0 0 5px rgba(242, 132, 130, 0.5), 0 0 20px rgba(242, 132, 130, 0.3)',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'progress': 'progress 1s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        progress: {
          '0%': { backgroundPosition: '1rem 0' },
          '100%': { backgroundPosition: '0 0' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}