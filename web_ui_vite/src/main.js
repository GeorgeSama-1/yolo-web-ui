import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

const app = createApp(App)

app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err)
  // Display error on screen
  const errorDiv = document.createElement('div')
  errorDiv.style.position = 'fixed'
  errorDiv.style.top = '0'
  errorDiv.style.left = '0'
  errorDiv.style.width = '100%'
  errorDiv.style.height = '100%'
  errorDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.9)'
  errorDiv.style.color = 'white'
  errorDiv.style.padding = '20px'
  errorDiv.style.zIndex = '9999'
  errorDiv.style.overflow = 'auto'
  errorDiv.style.whiteSpace = 'pre-wrap'
  errorDiv.style.fontFamily = 'monospace'
  errorDiv.innerHTML = `<h1>Application Error</h1><p>${err.toString()}</p><p>Info: ${info}</p><p>Stack: ${err.stack}</p>`
  document.body.appendChild(errorDiv)
}

window.addEventListener('error', (event) => {
  const errorDiv = document.createElement('div')
  errorDiv.style.position = 'fixed'
  errorDiv.style.bottom = '0'
  errorDiv.style.left = '0'
  errorDiv.style.width = '100%'
  errorDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'
  errorDiv.style.color = 'yellow'
  errorDiv.style.padding = '10px'
  errorDiv.style.zIndex = '9999'
  errorDiv.innerText = 'Global Error: ' + event.message
  document.body.appendChild(errorDiv)
})

app.mount('#app')
