import { app } from '../../scripts/app.js';

/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
    close: 'Close',
    working: 'Working...',
    settings: {
        close: 'Close Dreamina Settings',
        invalidDefinition: 'ComfyUI returned an invalid Dreamina setting definition.',
        invalidLimit: 'ComfyUI returned an invalid Dreamina limit.',
        invalidResponse: 'ComfyUI returned an invalid Dreamina Settings response.',
        limits: 'Request limits',
        limitsSaved: 'Limits saved.',
        menu: 'Dreamina Settings',
        noLimitChanges: 'No limit changes to save.',
        readFailed: 'ComfyUI could not read Dreamina Settings.',
        readOnly: "Changes are disabled in this host's multi-user mode.",
        reading: 'Loading settings...',
        reload: 'Reload settings',
        reread: 'Settings loaded.',
        saveFailed: 'ComfyUI could not save the Dreamina settings.',
        saveLimits: 'Save limits',
        title: 'Dreamina Settings',
        unreachable: 'Cannot reach Dreamina Settings. Check that ComfyUI is running, then select Reload settings.',
        unreadableResponse: 'ComfyUI returned an unreadable Dreamina Settings response.',
        updateFailed: 'The Dreamina settings could not be saved.',
    },
    cli: {
        confirmInstall:
            "Install the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
        confirmUpdate:
            "Update the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
        current: 'Dreamina CLI {version} is installed.',
        install: 'Install',
        installFailed: 'ComfyUI could not install the Dreamina CLI.',
        installed: 'Dreamina CLI installed.',
        installing: 'Installing the Dreamina CLI. This can take a few minutes...',
        legend: 'Dreamina CLI',
        missing: 'The Dreamina CLI is not installed on the ComfyUI computer. Select Install.',
        outdated:
            'Dreamina CLI {version} is installed, but the extension needs version {minimum} or later. Select Update.',
        update: 'Update',
    },
    account: {
        code: 'On the Dreamina sign-in page, check that it shows this code, then approve the sign-in:',
        expired: 'The sign-in link expired. Select Sign in to get a new one.',
        incomplete: 'The sign-in did not finish. Select Sign in to try again.',
        legend: 'Account',
        noCli: 'Install the Dreamina CLI, then sign in here.',
        notice: 'Your sign-in stays in the Dreamina CLI on the ComfyUI computer. The extension never sees your password or sign-in tokens.',
        openPage: 'Open the sign-in page',
        plan: 'Plan: {level}',
        signIn: 'Sign in',
        signInDone: 'Signed in.',
        signInFailed: 'ComfyUI could not start the Dreamina sign-in.',
        signInStarted: 'Sign-in started. Approve it on the Dreamina page.',
        signOut: 'Sign out',
        signOutDone: 'Signed out.',
        signOutFailed: 'ComfyUI could not sign out of Dreamina.',
        signedIn: 'Signed in to Dreamina.',
        signedOut: 'Sign in with your Dreamina account to run the Dreamina nodes.',
        until: 'The link works until {time}.',
    },
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
    ['max_download_megabytes', 'Maximum download size (MB)'],
    ['max_upload_megabytes', 'Maximum upload size (MB)'],
    ['request_timeout_seconds', 'Request timeout (seconds)'],
]);

type MessagePaths<Messages> = {
    [Key in keyof Messages & string]: Messages[Key] extends string ? Key : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;

/**
 * Read one message.
 *
 * @param key - A dotted path into the extension's text.
 * @returns The text at that path.
 */
export function message(key: MessageKey): string {
    let value: unknown = TEXT;
    for (const part of key.split('.')) {
        value = (value as Record<string, unknown>)[part];
    }
    return String(value);
}

/**
 * Read one message and fill its named placeholders.
 *
 * @param key - A dotted path into the extension's text.
 * @param values - The text for each placeholder name.
 * @returns The message with every known placeholder replaced.
 */
export function formatMessage(key: MessageKey, values: Readonly<Record<string, string>>): string {
    const replacements = new Map(Object.entries(values));
    return message(key).replaceAll(/\{(\w+)\}/g, (placeholder, name: string) => replacements.get(name) ?? placeholder);
}

/**
 * Read the language ComfyUI shows, which the server's messages follow.
 *
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
    const value = app.extensionManager.setting.get('Comfy.Locale');
    try {
        return Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ?? 'en';
    } catch {
        return 'en';
    }
}
