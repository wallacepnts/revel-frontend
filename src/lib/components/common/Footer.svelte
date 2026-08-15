<script lang="ts">
	import { resolve } from '$app/paths';
	import { env } from '$env/dynamic/public';
	import { appStore } from '$lib/stores/app.svelte';
	import Instagram from '$lib/components/icons/brand/Instagram.svelte';
	import Youtube from '$lib/components/icons/brand/Youtube.svelte';
	import * as m from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import RevelWordmark from '$lib/components/brand/RevelWordmark.svelte';

	// Shared link treatment for the inverted band: this surface is a dark one
	// in BOTH themes (ink in light, deepened card in dark — see the <footer>
	// class below), so "muted" text needs its own recipe per side rather than
	// the usual muted-foreground token (which assumes a light-mode-light /
	// dark-mode-dark surface). Light: text-background/70 on the opaque ink bg
	// measures 8.05:1 (full text-background is 15.43:1) — see the <footer>
	// comment for the base numbers this scales from. Dark: bg-card is a normal
	// themed surface, so muted-foreground/foreground on it are the SAME
	// audited pairs used everywhere else (card-foreground/muted-foreground on
	// card, both >= 4.5:1 in audit-brand-themes.py).
	const footerLinkClass =
		'text-background/70 transition-colors hover:text-background dark:text-muted-foreground dark:hover:text-foreground';

	// Frontend version from environment variable (set in Dockerfile).
	// Read via $env/dynamic/public so it has no compile-time requirement —
	// a checkout without a populated .env still type-checks and falls back to 'dev'.
	// Remove leading 'v' if present since we add it in the template.
	const FRONTEND_VERSION = env.PUBLIC_VERSION ? env.PUBLIC_VERSION.replace(/^v/, '') : 'dev';

	// Get backend version and demo mode from store
	const backendVersion = $derived(appStore.backendVersion || 'Loading...');
	const isDemoMode = $derived(appStore.isDemoMode);

	// Landing page URLs based on current locale
	// Landing pages are NOT paraglide-translated, they use /de/ and /it/ prefixes
	const landingPagePrefix = $derived(getLocale() === 'en' ? '' : `/${getLocale()}`);
</script>

<!-- Inverted "band" echoing the poster ClosePanel: dark surface in BOTH
     themes (ink in light, deepened card in dark — never a near-white band,
     per the imagery rule the dark side must still read as a dark surface). -->
<footer
	class="bg-foreground text-background dark:border-t dark:border-border dark:bg-card dark:text-card-foreground"
>
	<div class="container mx-auto max-w-5xl px-4 py-10 md:py-14">
		<!-- Brand lockup: the SAME RevelWordmark the header renders, so the
		     wordmark reads identically in the navbar and at the bottom of the
		     page (it used to be hand-set here, and drifted off the guide).
		     The colour lockup, not `mono`: this band is dark, but so is the
		     whole app in dark mode, and the gradient mark has always carried
		     colour here — the knockout variant is for surfaces the gradient
		     cannot read on (the poster's brand-gradient panel), not for every
		     dark background. "let's" and the period are currentColor, so they
		     take this band's inverted foreground, which is what the guide asks
		     of them on dark.
		     Visible text is the link's accessible name (WCAG 2.5.3).
		     text-background on bg-foreground mirrors the audited
		     foreground-on-background pair (contrast is symmetric): 15.43:1 in
		     light; dark reuses the audited card-foreground-on-card pair
		     (foreground === card-foreground in this theme). -->
		<a href={resolve('/(public)', {})} class="mb-8 inline-flex transition-opacity hover:opacity-80">
			<RevelWordmark />
		</a>

		<div class="grid grid-cols-2 gap-8 md:grid-cols-4">
			<!-- Solutions - spans 2 columns on md+ -->
			<div class="col-span-2">
				<h3 class="mb-4 text-lg font-extrabold">{m['footer.solutionsTitle']()}</h3>
				<div class="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/eventbrite-alternative" class={footerLinkClass}>
						{m['footer.solutionEventbrite']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/privacy-focused-events" class={footerLinkClass}>
						{m['footer.solutionPrivacy']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/self-hosted-event-platform" class={footerLinkClass}>
						{m['footer.solutionSelfHosted']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/community-first-event-platform" class={footerLinkClass}>
						{m['footer.solutionCommunity']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/queer-event-management" class={footerLinkClass}>
						{m['footer.solutionQueer']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
					<!-- eslint-disable svelte/no-navigation-without-resolve -- locale-prefixed landing path; the prefix comes from getLocale() and cannot map to a single static route id -->
					<a href="{landingPagePrefix}/kink-event-ticketing" class={footerLinkClass}>
						{m['footer.solutionKink']()}
					</a>
					<!-- eslint-enable svelte/no-navigation-without-resolve -->
				</div>
			</div>

			<!-- Legal Links -->
			<div>
				<h3 class="mb-4 text-lg font-extrabold">{m['footer.legalTitle']()}</h3>
				<ul class="space-y-2 text-sm">
					<li>
						<a href={resolve('/(public)/legal/privacy', {})} class={footerLinkClass}>
							{m['footer.privacyPolicy']()}
						</a>
					</li>
					<li>
						<a href={resolve('/(public)/legal/terms', {})} class={footerLinkClass}>
							{m['footer.termsOfService']()}
						</a>
					</li>
					<!-- DuRock: o e-mail de contato do upstream não atende ninguém
					     daqui. Volta quando houver um endereço do DuRock. -->
					<li>
						<a href="mailto:contato@durockrj.com.br" class={footerLinkClass}>
							{m['footer.contact']()}
						</a>
					</li>
				</ul>
			</div>

			<!-- Resources -->
			<div>
				<h3 class="mb-4 text-lg font-extrabold">{m['footer.resourcesTitle']()}</h3>
				<ul class="space-y-2 text-sm">
					<li>
						<a href={resolve('/(public)/shows', {})} class={footerLinkClass}>
							{m['nav.browseEvents']()}
						</a>
					</li>
					<li>
						<a href={resolve('/(public)/organizations', {})} class={footerLinkClass}>
							{m['nav.organizations']()}
						</a>
					</li>
					<!-- Redes do DuRock. Os rótulos são nomes próprios, iguais em
					     qualquer idioma, então não passam pelo catálogo: uma chave
					     nova exigiria os seis locales para dizer "Instagram".
					     O ícone herda currentColor em vez de usar a cor da marca —
					     esta faixa é invertida, e um roxo do Instagram sobre ela
					     não passaria no contraste que o resto do rodapé cumpre. -->
					<li>
						<a
							href="https://instagram.com/durockrj"
							target="_blank"
							rel="noopener noreferrer"
							class="{footerLinkClass} inline-flex items-center gap-2"
						>
							<Instagram class="h-4 w-4" aria-hidden="true" />
							Instagram
						</a>
					</li>
					<li>
						<a
							href="https://youtube.com/@durockrj"
							target="_blank"
							rel="noopener noreferrer"
							class="{footerLinkClass} inline-flex items-center gap-2"
						>
							<!-- i18n-ignore: nome próprio da plataforma, igual em todo idioma -->
							<Youtube class="h-4 w-4" aria-hidden="true" />
							YouTube
						</a>
					</li>
				</ul>
			</div>
		</div>

		<!-- Version strip. DuRock: sem tooltip de notas de release — o original
		     buscava na API do GitHub do letsrevel a cada visita de cada pessoa,
		     de um repositório que não é o desta instância. A versão continua
		     visível, que é o que serve para suporte. -->
		<div
			class="mt-8 flex flex-wrap items-center justify-center gap-4 border-t border-background/20 pt-6 text-xs text-background/70 dark:border-border dark:text-muted-foreground"
		>
			<span>FE v{FRONTEND_VERSION}</span>
			<span class="text-background/45 dark:text-muted-foreground/50">|</span>
			<span>BE v{backendVersion}{isDemoMode ? ' (demo)' : ''}</span>
		</div>

		<!-- Cookie Notice. Light: bg-background/10 (surface) composited over the
		     opaque ink band, then text-background/90 composited over THAT
		     surface (not directly over the ink) — 9.91:1 (re-verified; an
		     earlier draft of this comment mistakenly quoted the full-opacity
		     text number, 11.85:1). Dark keeps the original muted/50-on-card
		     treatment (7.04:1, hand-verified) since that's already a themed,
		     non-inverted surface. -->
		<div class="mt-8 border-t border-background/20 pt-8 dark:border-border">
			<div
				class="rounded-lg bg-background/10 p-4 text-center text-sm text-background/90 dark:bg-muted/50 dark:text-muted-foreground"
			>
				<p>
					{m['footer.cookieNotice']()}
				</p>
			</div>
		</div>

		<!-- Copyright -->
		<div class="mt-6 text-center text-sm text-background/70 dark:text-muted-foreground">
			<p>&copy; {new Date().getFullYear()} DuRock RJ. {m['footer.copyright']()}</p>
		</div>
	</div>
</footer>
