/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './static/templates/**/*.{html,js}',
    './auctions/templates/**/*.{html,js}',
    './auctions_ai/templates/**/*.{html,js}'
  ],
  theme: {
    extend: {
      maxHeight: {
        '128': '32rem'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
