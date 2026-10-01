/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0b1120',
        cardBg: '#1e293b',
        accentYellow: '#f59e0b',
      }
    },
  },
  plugins: [],
}