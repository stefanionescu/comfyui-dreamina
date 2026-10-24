import { button, element } from '#web/dom.ts';
import { browserRoutes } from '#web/routes.ts';
import { message, formatMessage } from '#web/text.ts';
import type { CliStatus } from '#web/settings/schema.ts';

/** What the Dreamina CLI part asks of the dialog. */
type CliActions = {
    update: (success: string, route: string, method: string, working: string) => void;
};

/** The Dreamina CLI part: whether the server finds the CLI, and Install or Update. */
export class CliSection {
    readonly form = element('form');

    readonly fields = element('fieldset');

    private readonly state = element('p');

    private readonly action = button(message('cli.install'), 'submit');

    private found = false;

    /**
     * Build the part without contacting the server.
     *
     * @param actions - The dialog's request for the part's button.
     */
    constructor(private readonly actions: CliActions) {
        this.fields.disabled = true;
        this.fields.append(element('legend', message('cli.legend')), this.state, this.action);
        this.form.append(this.fields);
        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            this.confirmInstall();
        });
    }

    /** Ask before ByteDance's official installer runs, then send the install; a cancel sends nothing. */
    private confirmInstall(): void {
        const question = message(this.found ? 'cli.confirmUpdate' : 'cli.confirmInstall');

        if (!globalThis.confirm(question)) return;
        this.actions.update(message('cli.installed'), browserRoutes.settings.cli, 'POST', message('cli.installing'));
    }

    /**
     * Show whether the server finds the CLI and whether it is current, and name the button for it.
     *
     * @param cli - The CLI part of the last status.
     */
    display(cli: CliStatus): void {
        this.found = cli.found;
        const version = cli.version ?? '';
        let text = message('cli.missing');
        if (cli.found && cli.isCurrent) text = formatMessage('cli.current', { version });
        else if (cli.found) {
            text = formatMessage('cli.outdated', { version, minimum: cli.minimumVersion });
        }
        this.state.replaceChildren(document.createTextNode(text));
        this.action.replaceChildren(document.createTextNode(message(cli.found ? 'cli.update' : 'cli.install')));
    }
}
