<script lang="ts">
	// DuRock RJ monogram — a "D" whose right stem forms the "R".
	//
	// Bitmap on purpose, for now: the brand exists only as PNG and the proper
	// vector is coming from the designer. Two files rather than one recoloured
	// by CSS, because a bitmap cannot inherit currentColor: favicon-light.png
	// is the ink mark for light surfaces, favicon-dark.png the white knockout
	// for dark ones, and the `.dark` class picks between them. Both are 256px
	// square, which is 8x the header's 32px — retina-safe where it is actually
	// used. When the SVG lands, this component is the only file that changes.
	//
	// Same props as the upstream mark it replaces (see vite.config.ts), so the
	// five call sites need no edit. `gradient` is accepted and ignored: the
	// monogram is flat by design. The --logo-from/--logo-to tokens still drive
	// the ticket header band, which is not this component.
	interface Props {
		/** Accepted for API parity with the mark this replaces; the monogram is flat. */
		gradient?: boolean;
		class?: string;
		title?: string;
		/** Decorative: hide from assistive tech (use when adjacent text names it). */
		decorative?: boolean;
	}
	const { class: className = '', title = 'DuRock RJ', decorative = false }: Props = $props();
</script>

<img
	src="/favicon-light.png"
	alt={decorative ? '' : title}
	aria-hidden={decorative ? 'true' : undefined}
	class="{className} dark:hidden"
	width="256"
	height="256"
	decoding="async"
/>
<img
	src="/favicon-dark.png"
	alt={decorative ? '' : title}
	aria-hidden={decorative ? 'true' : undefined}
	class="{className} hidden dark:block"
	width="256"
	height="256"
	decoding="async"
/>
