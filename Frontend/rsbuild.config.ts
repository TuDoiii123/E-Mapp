import { defineConfig, loadEnv } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import path from 'path';

// rsbuild mặc định chỉ expose biến prefix PUBLIC_. Source code dùng VITE_* nên
// phải nạp thủ công (đọc từ .env lẫn process.env) rồi inline qua source.define.
const { publicVars } = loadEnv({ prefixes: ['VITE_', 'PUBLIC_'] });

export default defineConfig({
  plugins: [pluginReact()],

  source: {
    entry: { index: './src/main.tsx' },
    define: publicVars,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  html: {
    template: './index.html',
  },

  server: {
    port: 3000,
    open: true,
  },

  output: {
    distPath: { root: 'build' },
    target: 'web',
  },
});
