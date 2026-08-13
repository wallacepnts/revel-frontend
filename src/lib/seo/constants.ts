export const LANGS = ['en', 'de', 'it', 'fr', 'es', 'pt'] as const;
export type Lang = (typeof LANGS)[number];

export const X_DEFAULT = 'x-default' as const;

export const OG_LOCALE: Record<Lang, string> = {
	en: 'en_US',
	de: 'de_DE',
	it: 'it_IT',
	fr: 'fr_FR',
	es: 'es_ES',
	pt: 'pt_PT'
};

// The instance's identity, configurable so a self-hosted deployment does not
// have to patch source to carry its own name — same reasoning as
// PUBLIC_DEFAULT_LANGUAGE. `$env/dynamic/public` rather than `static`: it is
// what api.ts and i18n.ts already use, it is read at runtime (so one image
// serves any instance), and an unset variable is simply undefined instead of
// a build error. vitest.setup.ts mocks it to `{}`, so tests get the defaults.
import { env } from '$env/dynamic/public';

export const SITE_NAME = env.PUBLIC_SITE_NAME || 'Revel';
export const TWITTER_SITE = env.PUBLIC_TWITTER_SITE || '@letsrevel';

// Versioned shareable assets (in static/). They are served with a 1-year
// immutable cache and scrapers (LinkedIn, Facebook, …) key their image
// caches by URL, so replacing the bytes in place is invisible to them.
// When the artwork changes: add a new file with a bumped suffix, point the
// constant at it, and keep the old file for already-scraped pages (#623).
export const OG_IMAGE_PATH = '/og-image-v2.png';
export const OG_LOGO_PATH = '/og-logo-v1.png';
