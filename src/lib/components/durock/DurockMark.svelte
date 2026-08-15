<script lang="ts">
	// DuRock RJ monogram — a "D" whose right stem forms the "R".
	//
	// Bitmap on purpose, for now: the brand exists only as PNG and the proper
	// vector is coming from the designer. One file inverted by CSS in dark
	// mode, which is exactly what durockrj.com.br serves — logo-mark.png is
	// the monogram bleeding to its own edges, so it FILLS the box it is given.
	// The favicon PNGs carry the icon safe-zone padding baked in, and using
	// them here rendered the mark visibly smaller inside the same 32px header
	// slot. `invert` works because the mark is flat black on transparent: the
	// filter flips RGB and leaves alpha alone.
	// When the SVG lands, this component is the only file that changes.
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
	src="/logo-mark.png"
	alt={decorative ? '' : title}
	aria-hidden={decorative ? 'true' : undefined}
	class="{className} dark:invert"
	width="622"
	height="652"
	decoding="async"
/>
