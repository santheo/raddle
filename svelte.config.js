import adapter from '@sveltejs/adapter-static'; // Change from adapter-auto to adapter-static
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Keep the preprocess setting from your original config
	preprocess: [vitePreprocess()],
	
	kit: {
		// Replace the adapter configuration
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html',
			precompress: false
		}),
		paths: {
			// Set this to your repository name if not using a custom domain
			// For example, if your repo is 'yourusername/raddle', use '/raddle'
			// Leave empty if you're using a custom domain
			base: ''
		}
	},
	compilerOptions: {
	  runes: true
	}
};

export default config;