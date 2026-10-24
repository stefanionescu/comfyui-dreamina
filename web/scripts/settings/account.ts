import { browserRoutes } from '#web/routes.ts';
import { browserLimits } from '#web/browser.ts';
import { button, element, externalLink } from '#web/dom.ts';
import type { Configuration } from '#web/settings/schema.ts';
import { message, formatMessage, selectedLocale } from '#web/text.ts';

/** What the Account part asks of the dialog. */
type AccountActions = {
    update: (success: string, route: string, method: string) => void;
    poll: () => Promise<Configuration | undefined>;
    report: (text: string) => void;
    signal: AbortSignal;
};

/**
 * Describe how a sign-in ended after the server stops waiting for it.
 *
 * @param configuration - The status read after the wait.
 * @returns The status line for the outcome.
 */
function describeOutcome(configuration: Configuration): string {
    if (configuration.account.signedIn) return message('account.signInDone');
    if (configuration.signIn?.state === 'expired') return message('account.expired');
    return configuration.signIn?.message ?? message('account.incomplete');
}

/**
 * Describe a pending sign-in: its code, its page, and when the link stops working.
 *
 * @param userCode - The code the person checks on the sign-in page.
 * @param url - The sign-in page, an https address the reply schema checked.
 * @param expiresAt - When the link stops working, in milliseconds.
 * @returns The lines the account part shows.
 */
function describeChallenge(userCode: string, url: string, expiresAt: number): HTMLElement[] {
    const code = element('p', userCode);
    code.className = 'dreamina-code';
    const link = element('p');
    link.append(externalLink(message('account.openPage'), url));
    const time = new Date(expiresAt).toLocaleTimeString(selectedLocale(), {
        hour: '2-digit',
        minute: '2-digit',
    });
    return [element('p', message('account.code')), code, link, element('p', formatMessage('account.until', { time }))];
}

/**
 * Describe the account part for the last status.
 *
 * @param configuration - The last status.
 * @returns The lines the account part shows.
 */
function describeAccount(configuration: Configuration): HTMLElement[] {
    const { cli, account, signIn } = configuration;
    if (!cli.found) return [element('p', message('account.noCli'))];
    if (account.signedIn) {
        const lines = [element('p', message('account.signedIn'))];
        if (account.vipLevel !== undefined) {
            lines.push(element('p', formatMessage('account.plan', { level: account.vipLevel })));
        }
        return lines;
    }
    if (signIn?.state === 'waiting') {
        return describeChallenge(signIn.userCode, signIn.verificationUrl, signIn.expiresAt);
    }
    if (signIn === undefined) return [element('p', message('account.signedOut'))];
    return [element('p', describeOutcome(configuration))];
}

/** The Account part: sign in with Dreamina's device code, follow the sign-in, or sign out. */
export class AccountSection {
    readonly form = element('form');

    readonly fields = element('fieldset');

    private readonly lines = element('div');

    private readonly signIn = button(message('account.signIn'), 'submit');

    private readonly signOut = button(message('account.signOut'));

    private timer: ReturnType<typeof setTimeout> | undefined;

    private isStarting = false;

    /**
     * Build the part without contacting the server.
     *
     * @param actions - The dialog's requests, its quiet status read, its status line, and its request lifetime,
     *     whose end stops following the sign-in.
     */
    constructor(private readonly actions: AccountActions) {
        this.fields.disabled = true;
        actions.signal.addEventListener('abort', () => {
            clearTimeout(this.timer);
        });
        const buttons = element('div');
        buttons.className = 'dreamina-actions';
        buttons.append(this.signIn, this.signOut);
        this.fields.append(element('legend', message('account.legend')), this.lines, buttons);
        this.form.append(this.fields);
        this.signOut.addEventListener('click', () => {
            this.actions.update(message('account.signOutDone'), browserRoutes.settings.session, 'DELETE');
        });
        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            this.isStarting = true;
            this.actions.update(message('account.signInStarted'), browserRoutes.settings.session, 'POST');
        });
    }

    /**
     * Read the status once more while a sign-in waits, and report how it ended.
     *
     * @returns When the dialog shows the read.
     */
    private async poll(): Promise<void> {
        this.timer = undefined;
        const configuration = await this.actions.poll();
        if (configuration === undefined || configuration.signIn?.state === 'waiting') return;
        this.actions.report(describeOutcome(configuration));
    }

    /**
     * Open the sign-in page once after Sign in, then read the status again while the sign-in waits.
     *
     * @param waiting - The sign-in that waits for the person, or undefined when none does.
     */
    private followSignIn(waiting: Configuration['signIn']): void {
        if (this.isStarting && waiting !== undefined) {
            window.open(waiting.verificationUrl, '_blank', 'noopener,noreferrer');
        }
        this.isStarting = false;
        if (waiting === undefined) {
            clearTimeout(this.timer);
            this.timer = undefined;
        } else {
            this.timer ??= setTimeout(() => {
                this.poll().catch(reportError);
            }, browserLimits.signInPollMilliseconds);
        }
    }

    /**
     * Show the account, open the sign-in page once after Sign in, and follow a waiting sign-in.
     *
     * @param configuration - The last status.
     */
    display(configuration: Configuration): void {
        const { cli, account, signIn } = configuration;
        const waiting = cli.found && !account.signedIn && signIn?.state === 'waiting' ? signIn : undefined;
        this.lines.replaceChildren(...describeAccount(configuration));
        this.signIn.hidden = !cli.found || account.signedIn || waiting !== undefined;
        this.signOut.hidden = !cli.found || !account.signedIn;
        this.followSignIn(waiting);
    }
}
