/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Brand palette — deep navy + saffron accent.
        brand: {
          50: "#eef4fb",
          100: "#d6e4f5",
          500: "#1e4e79",
          600: "#173d5f",
          700: "#0f2b46",
          900: "#081a2c",
        },
        saffron: {
          400: "#f59e0b",
          500: "#d97706",
          600: "#b45309",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(15,43,70,0.08), 0 1px 2px rgba(15,43,70,0.04)",
      },
    },
  },
  plugins: [],
};
