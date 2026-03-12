/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        danger: '#dc3545',
        success: '#28a745',
      },
      fontFamily: {
        sans: ['WenQuanYi Micro Hei', 'Microsoft YaHei', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
