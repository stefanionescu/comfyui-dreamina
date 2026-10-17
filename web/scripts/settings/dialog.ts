import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import { browserRoutes } from '#web/routes.ts';
import { CliSection } from '#web/settings/cli.ts';
import { AccountSection } from '#web/settings/account.ts';
import { requestConfiguration } from '#web/settings/api.ts';
import type { Configuration } from '#web/settings/schema.ts';
import { LIMIT_LABELS, message, setText } from '#web/text.ts';

let current: SettingsDialog | undefined;

/** Show the CLI, the account, and the request limits, and cancel pending requests when the dialog closes. */
class SettingsDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly status = element('p', message('settings.reading'));

  private readonly reload = button(message('settings.reload'));

  private readonly limitFields = element('fieldset');

  private readonly inputs = new Map<string, HTMLInputElement>();

  private readonly cli = new CliSection({
    update: (success, route, method, working) =>
      this.updateSettings(success, route, method, undefined, working),
  });

  private readonly account = new AccountSection({
    update: (success, route, method) => this.updateSettings(success, route, method),
    poll: () => this.pollStatus(),
    report: (text) => setText(this.status, text),
  });

  private configuration: Configuration | undefined;

  // Every request joins this chain, so the next one starts only after the last one settles.
  private pending: Promise<void> = Promise.resolve();

  /**
   * Build the dialog's parts without contacting the server.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(private readonly fetcher: Fetcher) {
    this.dialog.className = 'dreamina-dialog';
    this.dialog.setAttribute('aria-labelledby', 'dreamina-settings-title');
    const heading = element('h2', message('settings.title'));
    heading.id = 'dreamina-settings-title';
    const close = button(message('close'));
    close.setAttribute('aria-label', message('settings.close'));
    close.addEventListener('click', this.dialog.close.bind(this.dialog, undefined));
    const header = element('header');
    header.append(heading, close);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.reload.addEventListener('click', () => this.updateSettings(message('settings.reread')));
    const footer = element('footer');
    footer.append(this.status, this.reload);
    this.dialog.append(
      header,
      this.cli.form,
      this.account.form,
      element('p', message('account.notice')),
      this.limits(),
      footer,
    );
    this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
  }

  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  private limits(): HTMLFormElement {
    const form = element('form');
    this.limitFields.disabled = true;
    this.limitFields.append(element('legend', message('settings.limits')));
    this.limitFields.append(button(message('settings.saveLimits'), 'submit'));
    form.append(this.limitFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }

  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits.
   */
  private populateLimits(configuration: Configuration): void {
    this.limitFields.replaceChildren(element('legend', message('settings.limits')));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const label = element('label', LIMIT_LABELS.get(name) ?? name);
      const input = element('input');
      input.type = 'number';
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = '1';
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      this.limitFields.append(label);
    }
    this.limitFields.append(button(message('settings.saveLimits'), 'submit'));
  }

  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  private saveLimits(configuration: Configuration): void {
    const changes = new Map<string, number>();
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== settings.get(name)) changes.set(name, input.valueAsNumber);
    }
    if (changes.size === 0) {
      setText(this.status, message('settings.noLimitChanges'));
      return;
    }
    this.updateSettings(message('settings.limitsSaved'), browserRoutes.settings.values, 'PATCH', {
      revision: configuration.revision,
      settings: Object.fromEntries(changes),
    });
  }

  /**
   * Show the validated status and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  private display(configuration: Configuration): void {
    this.configuration = configuration;
    if (this.inputs.size === 0) this.populateLimits(configuration);
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(settings.get(name));
    }
    this.cli.display(configuration.cli);
    this.account.display(configuration);
    if (!configuration.mutationAllowed) setText(this.status, message('settings.readOnly'));
  }

  /**
   * Queue a request after the last one, disabling the parts and showing its working text.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @param working - The text shown while the request runs.
   */
  private updateSettings(
    success: string,
    route?: string,
    method?: string,
    body?: unknown,
    working: string = message('working'),
  ): void {
    this.cli.fields.disabled = this.account.fields.disabled = this.limitFields.disabled = true;
    this.reload.disabled = true;
    setText(this.status, working);
    this.pending = this.pending.then(() => this.requestSettings(success, route, method, body));
  }

  /**
   * Apply the server response and restore editing after a settings request.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  private async requestSettings(
    success: string,
    route?: string,
    method?: string,
    body?: unknown,
  ): Promise<void> {
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body,
      );
      if (this.controller.signal.aborted) return;
      setText(this.status, success);
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message('settings.updateFailed'),
        );
    } finally {
      if (!this.controller.signal.aborted) {
        const isLocked = !this.configuration?.mutationAllowed;
        this.cli.fields.disabled = this.account.fields.disabled = isLocked;
        this.limitFields.disabled = isLocked;
        this.reload.disabled = false;
      }
    }
  }

  /**
   * Read the status quietly while a sign-in waits, changing only the CLI and account parts.
   * @returns The status, or undefined after an error, which the status line then shows.
   */
  private pollStatus(): Promise<Configuration | undefined> {
    const reply = this.pending.then(async () => {
      try {
        const value = await requestConfiguration(this.fetcher, this.controller.signal);
        if (this.controller.signal.aborted) return undefined;
        this.cli.display(value.cli);
        this.account.display(value);
        return value;
      } catch (error) {
        if (!this.controller.signal.aborted)
          setText(
            this.status,
            error instanceof Error ? error.message : message('settings.readFailed'),
          );
        return undefined;
      }
    });
    this.pending = reply.then(() => undefined);
    return reply;
  }

  /** Show the dialog and read the status. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateSettings(message('settings.reread'));
  }

  /** Stop requests and the sign-in poll, and return focus to the caller. */
  private dispose(): void {
    this.account.dispose();
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one settings dialog at a time.
 * @param fetcher - ComfyUI's local API client.
 */
export function openSettings(fetcher: Fetcher): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new SettingsDialog(fetcher);
  current.show();
}
