import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
    plugins: [vue()],
    server: {
        port: 5000,
        host: '0.0.0.0',
        watch: {
            usePolling: true,
            interval: 300,
        },
        hmr: {
            protocol: 'ws',
            host: '0.0.0.0',
            port: 5000,
            clientPort: 5000
        }
    },
    root: 'public',
    resolve: {
        alias: {
            '/src': path.resolve(__dirname, 'src'),
            '@': path.resolve(__dirname, 'src')
        }
    },
    define: {
        'process.env': {}
    }
})
