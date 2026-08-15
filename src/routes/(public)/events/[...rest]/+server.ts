/**
 * Permanent redirect from the old `/events` paths to `/shows`.
 *
 * DuRock is a rock listing, so the public route is `/shows` — but `/events`
 * cannot simply disappear, because it is not only an old bookmark:
 *
 *   - the BACKEND builds `${FRONTEND_BASE_URL}/events/...` in five places
 *     (events/signals.py, announcement_service.py, follow_service.py), so
 *     every notification e-mail already sent — and every one it sends until
 *     that repo changes — points here;
 *   - stripe_service.py uses `/events/{org}/{event}` as the checkout
 *     success_url AND cancel_url, so dropping this route would strand buyers
 *     on a 404 right after paying;
 *   - the old URLs are in Google's index and in whatever people have shared.
 *
 * `[...rest]` matches zero segments too, so `/events` itself lands here. The
 * query string is forwarded verbatim — Stripe's `?payment_success=true` and
 * the shareable `?et=<token>` links both carry state we must not drop.
 *
 * 301 rather than 302 so search engines transfer the ranking to `/shows`.
 */
import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = ({ params, url }) => {
	const rest = params.rest ? `/${params.rest}` : '';
	redirect(301, `/shows${rest}${url.search}`);
};
