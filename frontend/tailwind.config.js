/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#faf4ff',
        surface: '#faf4ff',
        'surface-container': '#ede4ff',
        'surface-container-low': '#f5eeff',
        'surface-container-lowest': '#ffffff',
        'surface-container-high': '#e8deff',
        'surface-container-highest': '#e2d7ff',
        primary: '#4a40e0',
        'primary-dim': '#3d30d4',
        'primary-container': '#9795ff',
        'on-primary': '#f4f1ff',
        'on-surface': '#32294f',
        'on-surface-variant': '#5f557f',
        'secondary-container': '#65e1ff',
        'on-secondary-container': '#004f5d',
        tertiary: '#b80438',
        'outline-variant': '#b2a6d5',
      },
      fontFamily: {
        manrope: ['Manrope', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
