/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: '#060a18',    // page background
        panel: '#0a1124',  // sidebar and top bar
        card: '#0e1630',   // cards
        line: '#1a2342',   // borders
        brand: { DEFAULT: '#ffb800', soft: '#ffc933' },
        // Old names, kept so nothing else in the project breaks
        darkBg: '#060a18',
        cardBg: '#0e1630',
        accentYellow: '#ffb800',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
