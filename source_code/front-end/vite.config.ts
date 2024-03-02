import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    /*(1) uncomment below to use electron */
    /*(2) use another json*/
    // electron({
    //   entry: 'electron/main.ts'
    // }),
  ],
})
