<script lang="ts">
	// DuRock RJ lockup — the DR monogram plus the name. Replaces the upstream
	// "let's revel." wordmark at every call site through the resolveId swap in
	// vite.config.ts, so Header, Footer and the three landing panels pick it up
	// without any of them being edited.
	//
	// Props are the upstream contract, unchanged, because the call sites are
	// upstream's: `mono` is the flat white-on-dark knockout (used over coloured
	// panels where a gradient would disappear), `mark={false}` drops the
	// monogram, and size is inherited — `class` overrides the text-2xl default
	// through tailwind-merge, so the same lockup scales from the navbar to
	// poster type.
	//
	// "DuRock" carries the weight and "RJ" sits lighter beside it: the city is
	// context, not the name. The monogram is decorative because the visible
	// text already names the brand — announcing it twice is WCAG 2.5.3 noise.
	import { cn } from '$lib/utils';
	import DurockMark from './DurockMark.svelte';

	interface Props {
		class?: string;
		/** Flat currentColor knockout for dark or coloured surfaces. */
		mono?: boolean;
		/** Render the DR monogram beside the name. */
		mark?: boolean;
	}
	const { class: className = '', mono = false, mark = true }: Props = $props();

	// "Du" and "RJ" in gold, as durockrj.com.br has always shown them — but
	// through --accent-text, not --accent: the fill gold measures 2.40:1 on
	// white paper, below even the 3:1 large-text floor. `mono` is the knockout
	// for coloured panels, where any hue would fight the panel, so it stays flat.
	const gold = mono ? '' : 'text-[hsl(var(--accent-text))]';
</script>

<span class={cn('inline-flex items-center gap-2 text-2xl leading-none', className)}>
	{#if mark}
		<DurockMark decorative gradient={!mono} class="h-[1em] w-auto" />
	{/if}
	<span class="tracking-tight">
		<span class="font-extrabold"><span class={gold}>Du</span>Rock</span>
		<span class="font-light {gold}">RJ</span>
	</span>
</span>
