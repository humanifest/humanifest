import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import { resolve } from 'path';
export default defineConfig({
    base: './',
    envDir: resolve('humanifest-probes'),
    plugins: [react(), nodePolyfills({ globals: { Buffer: true, global: true, process: true }, protocolImports: true })],
    define: { 'process.env.NODE_ENV': JSON.stringify('production'), 'process.version': JSON.stringify('v22.22.0'), __dirname: JSON.stringify('/'), __filename: JSON.stringify('/index.js') },
    esbuild: { define: { global: 'globalThis' } },
    resolve: { alias: [{ find: '@peculiar/webcrypto', replacement: resolve('src/utils/shims/webcrypto-browser.js') }] },
    build: { outDir: 'humanifest-ui-dist', rollupOptions: { input: resolve('humanifest-probes/global-mapping-ui.html') } },
});
