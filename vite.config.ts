import { sveltekit } from '@sveltejs/kit/vite';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig, type Plugin } from 'vitest/config';

// DuRock RJ: swap the upstream brand lockup for this fork's, without editing a
// single upstream component. Five call sites import the mark and the wordmark
// (Header, Footer, and three landing panels); this rewrites the resolution of
// those two module ids, so every one of them draws the DuRock monogram.
//
// It is a resolveId hook rather than a `resolve.alias` entry because alias
// matching happens before SvelteKit turns `$lib/...` into a real path, and a
// `kit.alias` entry for an exact file was tried first and did NOT take effect —
// `$lib` won. Matching the RESOLVED path is order-independent, so it holds no
// matter how SvelteKit orders its own aliases.
const BRAND_SWAPS: Record<string, string> = {
	'src/lib/components/brand/RevelWordmark.svelte':
		'src/lib/components/durock/DurockWordmark.svelte',
	'src/lib/components/brand/RevelMark.svelte': 'src/lib/components/durock/DurockMark.svelte'
};

function durockBrand(): Plugin {
	const root = fileURLToPath(new URL('.', import.meta.url));
	return {
		name: 'durock-brand',
		enforce: 'pre',

		// A swap that stops matching fails SILENTLY: the import resolves to
		// upstream's component and the Revel logo comes back with no error at
		// all. The way that happens is upstream renaming or deleting one of
		// these files, which a rebase would carry in without a word. So assert
		// both ends exist before the build starts — a loud failure here beats a
		// production deploy wearing someone else's brand.
		configResolved() {
			const faltando = Object.entries(BRAND_SWAPS)
				.flatMap(([upstream, fork]) => [upstream, fork])
				.filter((caminho) => !existsSync(root + caminho));

			if (faltando.length > 0) {
				throw new Error(
					`[durock-brand] estes arquivos não existem mais:\n  ${faltando.join('\n  ')}\n` +
						`A troca da marca depende deles. Se o upstream renomeou o componente, ` +
						`atualize BRAND_SWAPS em vite.config.ts — sem isso o site publica a marca do Revel.`
				);
			}
		},

		async resolveId(source, importer, options) {
			if (!source.includes('brand/Revel')) return null;
			const resolved = await this.resolve(source, importer, { ...options, skipSelf: true });
			if (!resolved) return null;
			for (const [upstream, fork] of Object.entries(BRAND_SWAPS)) {
				if (resolved.id.endsWith(upstream)) return root + fork;
			}
			return null;
		}
	};
}

// Under Vitest only, add the `svelte` resolve condition so bits-ui (which
// ships only `types` + `svelte` export conditions) resolves from its main
// entry. Outside Vitest we leave `resolve.conditions` undefined so Vite's
// defaults (`module`, `browser`, `default`, …) remain in force — overriding
// them here breaks client module resolution during SSR/hydration.
const viteResolve = process.env.VITEST ? { conditions: ['browser', 'svelte'] } : undefined;

export default defineConfig({
	plugins: [durockBrand(), sveltekit()],
	build: {
		// Skip gzip-size reporting: it adds build time and hundreds of log lines in CI
		reportCompressedSize: false
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['./vitest.setup.ts']
	},
	resolve: viteResolve,
	// Playwright's webServer starts `vite preview` and waits on port 5173; the
	// vite default (4173) left it timing out (see playwright.config.ts).
	preview: {
		port: 5173,
		strictPort: true
	},
	server: {
		host: '0.0.0.0', // Listen on all network interfaces for mobile testing
		port: 5173,
		strictPort: false,
		// Warmup Paraglide files during server startup to improve Firefox dev performance
		warmup: {
			clientFiles: ['./src/lib/paraglide/messages.js', './src/lib/paraglide/runtime.js']
		}
	}
});
