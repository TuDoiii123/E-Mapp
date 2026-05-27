import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [pluginReact()],

  source: {
    entry: { index: './src/main.tsx' },
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
