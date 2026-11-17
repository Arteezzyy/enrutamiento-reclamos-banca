/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0B2545',
          light: '#13315C',
          deep: '#081B33'
        },
        accent: {
          DEFAULT: '#1B998B',
          dark: '#157A6E',
          soft: '#E6F5F2'
        },
        gold: {
          DEFAULT: '#C9A227',
          dark: '#A07E14',
          soft: '#FBF5E2'
        },
        ink: '#1A2433',
        muted: '#5B6B7F',
        line: '#E3E8EF',
        app: '#F5F7FA'
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        display: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif']
      },
      boxShadow: {
        card: '0 1px 2px rgba(16, 24, 40, 0.04), 0 10px 26px -18px rgba(16, 24, 40, 0.28)',
        lift: '0 24px 48px -24px rgba(11, 37, 69, 0.45)'
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(16px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' }
        }
      },
      animation: {
        'fade-up': 'fade-up 0.35s ease-out both',
        'slide-up': 'slide-up 0.25s ease-out both'
      }
    }
  },
  plugins: []
}
