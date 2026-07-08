/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        saffron: '#FF9933',   // or your exact brand saffron hex
        cream: '#FFFDD0',     // light background tint
        ink: '#1A1A1A',       // dark text/headers
        stone: '#78716C',     // neutral descriptive text
        leaf: '#2E7D32',      // success / green buttons
        chakra: '#000080',    // secondary blue accents
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'], // As specified by font-display classes
      }
    },
  },
  plugins: [],
}