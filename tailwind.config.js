/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './static/templates/**/*.{html,js}',
    './auctions/templates/**/*.{html,js}',
    './auctions_ai/templates/**/*.{html,js}'
  ],
  theme: {
    extend: {}
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
