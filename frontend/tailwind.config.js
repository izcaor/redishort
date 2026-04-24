/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#020b1d',
        surface: '#04132b',
        'surface-container': '#082347',
        'surface-container-low': '#051b37',
        'surface-container-lowest': '#031227',
        'surface-container-high': '#0d2e5a',
        'surface-container-highest': '#16406f',
        primary: '#ff7a00',
        'primary-dim': '#f55b00',
        'primary-container': '#ffb061',
        'on-primary': '#04132b',
        'on-surface': '#e8f3ff',
        'on-surface-variant': '#9dc7ea',
        'secondary-container': '#1ecfff',
        'on-secondary-container': '#032338',
        tertiary: '#ff4f63',
        'outline-variant': '#2667a4',
      },
      boxShadow: {
        glow: '0 20px 50px rgba(3, 19, 39, 0.65)',
        brand: '0 10px 30px rgba(30, 207, 255, 0.2)',
      },
      fontFamily: {
        manrope: ['Manrope', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
