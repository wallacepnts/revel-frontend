<script lang="ts">
	// Two states, one click: dark ↔ light. `toggleMode` is mode-watcher's own
	// flip (`userPrefersMode = mode === 'dark' ? 'light' : 'dark'`), so there is
	// nothing to reimplement here.
	//
	// The dropdown this replaces offered a third option, "system", which never
	// worked as displayed: `mode.current` resolves to "dark" | "light" |
	// undefined and never to "system", so that row could not highlight and the
	// Monitor icon only ever appeared before hydration.
	//
	// Dropping the explicit choice does NOT force a mode on arrival: until the
	// visitor clicks, mode-watcher still follows the operating system. The click
	// is what pins a preference, which is the behaviour a two-state control
	// promises.
	import { mode, toggleMode } from 'mode-watcher';
	import { Sun, Moon } from '@lucide/svelte';
	import * as m from '$lib/paraglide/messages.js';

	const isDark = $derived(mode.current === 'dark');
</script>

<button
	type="button"
	class="inline-flex items-center justify-center rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-ring"
	onclick={toggleMode}
	aria-label={m['theme.toggleTheme']()}
	aria-pressed={isDark}
>
	{#if isDark}
		<Moon class="h-5 w-5" aria-hidden="true" />
	{:else}
		<Sun class="h-5 w-5" aria-hidden="true" />
	{/if}
</button>
