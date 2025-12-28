/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./templates/**/*.{html,js}",
    "./static/**/*.{html,js}",
  ],
  theme: {
    extend: {
      colors: {
        tesla: {
          black: "#0b0b0b",
          gray: "#6b6b6b",
          light: "#f7f7f7",
          muted: "#f0f0f0",
        },
      },
    },
  },
  plugins: [],
}
