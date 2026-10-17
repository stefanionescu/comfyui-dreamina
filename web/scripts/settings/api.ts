import type { Fetcher } from '#web/http.ts';
import { browserRoutes } from '#web/routes.ts';
import { browserLimits } from '#web/browser.ts';
import { parsePublicError } from '#web/schema.ts';
import { message, type MessageKey } from '#web/text.ts';
import { parseConfiguration, type Configuration } from '#web/settings/schema.ts';

/** The message for a failed request whose error body is unreadable, keyed by method and route. */
const FAILURES = new Map<string, MessageKey>([
  [`GET ${browserRoutes.settings.status}`, 'settings.readFailed'],
  [`POST ${browserRoutes.settings.session}`, 'account.signInFailed'],
  [`DELETE ${browserRoutes.settings.session}`, 'account.signOutFailed'],
  [`POST ${browserRoutes.settings.cli}`, 'cli.installFailed'],
]);

/**
 * Read or change settings through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The settings dialog's request lifetime.
 * @param route - The local settings route.
 * @param method - The HTTP method.
 * @param body - The settings change, if any.
 * @returns The validated status after the request.
 */
export async function requestConfiguration(
  fetcher: Fetcher,
  signal: AbortSignal,
  route: string = browserRoutes.settings.status,
  method: string = 'GET',
  body?: unknown,
): Promise<Configuration> {
  const timeout =
    route === browserRoutes.settings.cli
      ? browserLimits.installTimeoutMilliseconds
      : browserLimits.requestTimeoutMilliseconds;
  const options: RequestInit = {
    method,
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([signal, AbortSignal.timeout(timeout)]),
    headers: { 'Content-Type': 'application/json', 'X-Dreamina-Comfy': '1' },
  };
  if (body !== undefined) options.body = JSON.stringify(body);
  let response: Response;
  try {
    response = await fetcher(route, options);
  } catch {
    throw new Error(message('settings.unreachable'));
  }
  let document: unknown;
  try {
    document = await response.json();
  } catch {
    throw new Error(message('settings.unreadableResponse'));
  }
  if (!response.ok) {
    throw new Error(
      parsePublicError(document) ??
        message(FAILURES.get(`${method} ${route}`) ?? 'settings.saveFailed'),
    );
  }
  return parseConfiguration(document);
}
