// web/scripts/text.ts
import { app } from "../../scripts/app.js";
var TEXT = {
  close: "Close",
  working: "Working...",
  settings: {
    close: "Close Dreamina Settings",
    invalidDefinition: "ComfyUI returned an invalid Dreamina setting definition.",
    invalidLimit: "ComfyUI returned an invalid Dreamina limit.",
    invalidResponse: "ComfyUI returned an invalid Dreamina Settings response.",
    limits: "Request limits",
    limitsSaved: "Limits saved.",
    menu: "Dreamina Settings",
    noLimitChanges: "No limit changes to save.",
    readFailed: "ComfyUI could not read Dreamina Settings.",
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reading: "Loading settings...",
    reload: "Reload settings",
    reread: "Settings loaded.",
    saveFailed: "ComfyUI could not save the Dreamina settings.",
    saveLimits: "Save limits",
    title: "Dreamina Settings",
    unreachable: "Cannot reach Dreamina Settings. Check that ComfyUI is running, then select Reload settings.",
    unreadableResponse: "ComfyUI returned an unreadable Dreamina Settings response.",
    updateFailed: "The Dreamina settings could not be saved."
  },
  cli: {
    confirmInstall: "Install the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
    confirmUpdate: "Update the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
    current: "Dreamina CLI {version} is installed.",
    install: "Install",
    installFailed: "ComfyUI could not install the Dreamina CLI.",
    installed: "Dreamina CLI installed.",
    installing: "Installing the Dreamina CLI. This can take a few minutes...",
    legend: "Dreamina CLI",
    missing: "The Dreamina CLI is not installed on the ComfyUI computer. Select Install.",
    outdated: "Dreamina CLI {version} is installed, but the extension needs version {minimum} or later. Select Update.",
    update: "Update"
  },
  account: {
    code: "On the Dreamina sign-in page, check that it shows this code, then approve the sign-in:",
    expired: "The sign-in link expired. Select Sign in to get a new one.",
    incomplete: "The sign-in did not finish. Select Sign in to try again.",
    legend: "Account",
    noCli: "Install the Dreamina CLI, then sign in here.",
    notice: "Your sign-in stays in the Dreamina CLI on the ComfyUI computer. The extension never sees your password or sign-in tokens.",
    openPage: "Open the sign-in page",
    plan: "Plan: {level}",
    signIn: "Sign in",
    signInDone: "Signed in.",
    signInFailed: "ComfyUI could not start the Dreamina sign-in.",
    signInStarted: "Sign-in started. Approve it on the Dreamina page.",
    signOut: "Sign out",
    signOutDone: "Signed out.",
    signOutFailed: "ComfyUI could not sign out of Dreamina.",
    signedIn: "Signed in to Dreamina.",
    signedOut: "Sign in with your Dreamina account to run the Dreamina nodes.",
    until: "The link works until {time}."
  }
};
var LIMIT_LABELS = /* @__PURE__ */ new Map([
  ["max_download_megabytes", "Maximum download size (MB)"],
  ["max_upload_megabytes", "Maximum upload size (MB)"],
  ["request_timeout_seconds", "Request timeout (seconds)"]
]);
function message(key) {
  let value = TEXT;
  for (const part of key.split(".")) {
    value = value[part];
  }
  return String(value);
}
function formatMessage(key, values) {
  const replacements = new Map(Object.entries(values));
  return message(key).replaceAll(
    /\{(\w+)\}/g,
    (placeholder, name) => replacements.get(name) ?? placeholder
  );
}
function setText(target, content) {
  target.replaceChildren(document.createTextNode(content));
}
function selectedLocale() {
  const value = app.extensionManager.setting.get("Comfy.Locale");
  try {
    return Intl.getCanonicalLocales(typeof value === "string" ? value.replaceAll("_", "-") : "en")[0] ?? "en";
  } catch {
    return "en";
  }
}

// web/scripts/extension.ts
import { app as app2 } from "../../scripts/app.js";

// web/scripts/http.ts
import { api } from "../../scripts/api.js";
function requestLocal(route, options) {
  const headers = new Headers(options.headers);
  headers.set("Accept-Language", selectedLocale());
  return api.fetchApi(route, { ...options, headers });
}

// web/scripts/dom.ts
function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== void 0) node.appendChild(document.createTextNode(text));
  return node;
}
function button(text, type = "button") {
  const node = element("button", text);
  node.type = type;
  return node;
}
function externalLink(text, url2) {
  const node = element("a", text);
  node.href = url2;
  node.target = "_blank";
  node.rel = "noopener noreferrer";
  return node;
}

// web/scripts/routes.ts
var browserRoutes = {
  settings: {
    status: "/dreamina/v1/status",
    values: "/dreamina/v1/settings",
    session: "/dreamina/v1/session",
    cli: "/dreamina/v1/cli"
  }
};

// web/scripts/settings/cli.ts
var CliSection = class {
  /**
   * Build the part without contacting the server.
   * @param actions - The dialog's request for the part's button.
   */
  constructor(actions) {
    this.actions = actions;
    this.fields.disabled = true;
    this.fields.append(element("legend", message("cli.legend")), this.state, this.action);
    this.form.append(this.fields);
    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.confirmInstall();
    });
  }
  actions;
  form = element("form");
  fields = element("fieldset");
  state = element("p");
  action = button(message("cli.install"), "submit");
  found = false;
  /** Ask before ByteDance's official installer runs, then send the install; a cancel sends nothing. */
  confirmInstall() {
    const question = message(this.found ? "cli.confirmUpdate" : "cli.confirmInstall");
    if (!window.confirm(question)) return;
    this.actions.update(
      message("cli.installed"),
      browserRoutes.settings.cli,
      "POST",
      message("cli.installing")
    );
  }
  /**
   * Show whether the CLI is installed and current, and name the button for it.
   * @param cli - The CLI part of the last status.
   */
  display(cli) {
    this.found = cli.found;
    const version = cli.version ?? "";
    let text = message("cli.missing");
    if (cli.found && cli.isCurrent) text = formatMessage("cli.current", { version });
    else if (cli.found) {
      text = formatMessage("cli.outdated", { version, minimum: cli.minimumVersion });
    }
    setText(this.state, text);
    setText(this.action, message(cli.found ? "cli.update" : "cli.install"));
  }
};

// web/scripts/browser.ts
var browserLimits = {
  requestTimeoutMilliseconds: 6e4,
  installTimeoutMilliseconds: 39e4,
  signInPollMilliseconds: 2e3,
  maxErrorCharacters: 1024
};
var browserPatterns = {
  revision: /^[a-f0-9]{64}$/,
  settingName: /^[a-z][a-z_]+$/
};

// web/scripts/settings/account.ts
function describeOutcome(configuration) {
  if (configuration.account.signedIn) return message("account.signInDone");
  if (configuration.signIn?.state === "expired") return message("account.expired");
  return configuration.signIn?.message ?? message("account.incomplete");
}
function describeChallenge(userCode, url2, expiresAt) {
  const code = element("p", userCode);
  code.className = "dreamina-code";
  const link = element("p");
  link.append(externalLink(message("account.openPage"), url2));
  const time = new Date(expiresAt).toLocaleTimeString(selectedLocale(), {
    hour: "2-digit",
    minute: "2-digit"
  });
  return [
    element("p", message("account.code")),
    code,
    link,
    element("p", formatMessage("account.until", { time }))
  ];
}
function describeAccount(configuration) {
  const { cli, account, signIn } = configuration;
  if (!cli.found) return [element("p", message("account.noCli"))];
  if (account.signedIn) {
    const lines = [element("p", message("account.signedIn"))];
    if (account.vipLevel !== void 0) {
      lines.push(element("p", formatMessage("account.plan", { level: account.vipLevel })));
    }
    return lines;
  }
  if (signIn?.state === "waiting") {
    return describeChallenge(signIn.userCode, signIn.verificationUrl, signIn.expiresAt);
  }
  if (signIn === void 0) return [element("p", message("account.signedOut"))];
  return [element("p", describeOutcome(configuration))];
}
var AccountSection = class {
  /**
   * Build the part without contacting the server.
   * @param actions - The dialog's requests, its quiet status read, and its status line.
   */
  constructor(actions) {
    this.actions = actions;
    this.fields.disabled = true;
    const buttons = element("div");
    buttons.className = "dreamina-actions";
    buttons.append(this.signIn, this.signOut);
    this.fields.append(element("legend", message("account.legend")), this.lines, buttons);
    this.form.append(this.fields);
    this.signOut.addEventListener(
      "click",
      () => this.actions.update(message("account.signOutDone"), browserRoutes.settings.session, "DELETE")
    );
    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.isStarting = true;
      this.actions.update(message("account.signInStarted"), browserRoutes.settings.session, "POST");
    });
  }
  actions;
  form = element("form");
  fields = element("fieldset");
  lines = element("div");
  signIn = button(message("account.signIn"), "submit");
  signOut = button(message("account.signOut"));
  timer;
  isStarting = false;
  /**
   * Read the status once more while a sign-in waits, and report how it ended.
   * @returns When the read is shown.
   */
  async poll() {
    this.timer = void 0;
    const configuration = await this.actions.poll();
    if (configuration === void 0 || configuration.signIn?.state === "waiting") return;
    this.actions.report(describeOutcome(configuration));
  }
  /**
   * Show the account, open the sign-in page once after Sign in, and follow a waiting sign-in.
   * @param configuration - The last status.
   */
  display(configuration) {
    const { cli, account, signIn } = configuration;
    const waiting = cli.found && !account.signedIn && signIn?.state === "waiting" ? signIn : void 0;
    this.lines.replaceChildren(...describeAccount(configuration));
    this.signIn.hidden = !cli.found || account.signedIn || waiting !== void 0;
    this.signOut.hidden = !cli.found || !account.signedIn;
    if (this.isStarting && waiting !== void 0) {
      window.open(waiting.verificationUrl, "_blank", "noopener,noreferrer");
    }
    this.isStarting = false;
    if (waiting === void 0) this.dispose();
    else this.timer ??= setTimeout(() => void this.poll(), browserLimits.signInPollMilliseconds);
  }
  /** Stop following the sign-in. */
  dispose() {
    clearTimeout(this.timer);
    this.timer = void 0;
  }
};

// node_modules/valibot/dist/index.mjs
var store$4;
var DEFAULT_CONFIG = {
  lang: void 0,
  message: void 0,
  abortEarly: void 0,
  abortPipeEarly: void 0
};
// @__NO_SIDE_EFFECTS__
function getGlobalConfig(config$1) {
  if (!config$1 && !store$4) return DEFAULT_CONFIG;
  return {
    lang: config$1?.lang ?? store$4?.lang,
    message: config$1?.message,
    abortEarly: config$1?.abortEarly ?? store$4?.abortEarly,
    abortPipeEarly: config$1?.abortPipeEarly ?? store$4?.abortPipeEarly
  };
}
var store$3;
// @__NO_SIDE_EFFECTS__
function getGlobalMessage(lang) {
  return store$3?.get(lang);
}
var store$2;
// @__NO_SIDE_EFFECTS__
function getSchemaMessage(lang) {
  return store$2?.get(lang);
}
var store$1;
// @__NO_SIDE_EFFECTS__
function getSpecificMessage(reference, lang) {
  return store$1?.get(reference)?.get(lang);
}
// @__NO_SIDE_EFFECTS__
function _stringify(input) {
  const type = typeof input;
  if (type === "string") return `"${input}"`;
  if (type === "number" || type === "bigint" || type === "boolean") return `${input}`;
  if (type === "object" || type === "function") return (input && Object.getPrototypeOf(input)?.constructor?.name) ?? "null";
  return type;
}
function _addIssue(context, label, dataset, config$1, other) {
  const input = other && "input" in other ? other.input : dataset.value;
  const expected = other?.expected ?? context.expects ?? null;
  const received = other?.received ?? /* @__PURE__ */ _stringify(input);
  const issue = {
    kind: context.kind,
    type: context.type,
    input,
    expected,
    received,
    message: `Invalid ${label}: ${expected ? `Expected ${expected} but r` : "R"}eceived ${received}`,
    requirement: context.requirement,
    path: other?.path,
    issues: other?.issues,
    lang: config$1.lang,
    abortEarly: config$1.abortEarly,
    abortPipeEarly: config$1.abortPipeEarly
  };
  const isSchema = context.kind === "schema";
  const message$1 = other?.message ?? context.message ?? /* @__PURE__ */ getSpecificMessage(context.reference, issue.lang) ?? (isSchema ? /* @__PURE__ */ getSchemaMessage(issue.lang) : null) ?? config$1.message ?? /* @__PURE__ */ getGlobalMessage(issue.lang);
  if (message$1 !== void 0) issue.message = typeof message$1 === "function" ? message$1(issue) : message$1;
  if (isSchema) dataset.typed = false;
  if (dataset.issues) dataset.issues.push(issue);
  else dataset.issues = [issue];
}
// @__NO_SIDE_EFFECTS__
function _isValidObjectKey(object$1, key) {
  return Object.prototype.hasOwnProperty.call(object$1, key) && key !== "__proto__" && key !== "prototype" && key !== "constructor";
}
// @__NO_SIDE_EFFECTS__
function _joinExpects(values$1, separator) {
  const list = [...new Set(values$1)];
  if (list.length > 1) return `(${list.join(` ${separator} `)})`;
  return list[0] ?? "never";
}
function _standardSchema(schema) {
  schema["~standard"] = {
    version: 1,
    vendor: "valibot",
    validate: (value$1) => schema["~run"]({ value: value$1 }, /* @__PURE__ */ getGlobalConfig())
  };
  return schema;
}
var ISO_TIMESTAMP_REGEX = /^\d{4}-(?:0[1-9]|1[0-2])-(?:[12]\d|0[1-9]|3[01])[T ](?:0\d|1\d|2[0-3])(?::[0-5]\d){2}(?:\.\d{1,9})?(?:Z| ?[+-](?:0\d|1\d|2[0-3])(?::?[0-5]\d)?)$/u;
// @__NO_SIDE_EFFECTS__
function isoTimestamp(message$1) {
  return {
    kind: "validation",
    type: "iso_timestamp",
    reference: isoTimestamp,
    async: false,
    expects: null,
    requirement: ISO_TIMESTAMP_REGEX,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement.test(dataset.value)) _addIssue(this, "timestamp", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function maxLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_length",
    reference: maxLength,
    async: false,
    expects: `<=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length > this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function maxValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_value",
    reference: maxValue,
    async: false,
    expects: `<=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value <= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_length",
    reference: minLength,
    async: false,
    expects: `>=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length < this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_value",
    reference: minValue,
    async: false,
    expects: `>=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value >= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function regex(requirement, message$1) {
  return {
    kind: "validation",
    type: "regex",
    reference: regex,
    async: false,
    expects: `${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement.test(dataset.value)) _addIssue(this, "format", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function safeInteger(message$1) {
  return {
    kind: "validation",
    type: "safe_integer",
    reference: safeInteger,
    async: false,
    expects: null,
    requirement: Number.isSafeInteger,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "safe integer", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function startsWith(requirement, message$1) {
  return {
    kind: "validation",
    type: "starts_with",
    reference: startsWith,
    async: false,
    expects: `"${requirement}"`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !dataset.value.startsWith(this.requirement)) _addIssue(this, "start", dataset, config$1, { received: `"${dataset.value.slice(0, this.requirement.length)}"` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function url(message$1) {
  return {
    kind: "validation",
    type: "url",
    reference: url,
    async: false,
    expects: null,
    requirement(input) {
      try {
        if (URL.canParse) return URL.canParse(input);
        new URL(input);
        return true;
      } catch {
        return false;
      }
    },
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "URL", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function getFallback(schema, dataset, config$1) {
  return typeof schema.fallback === "function" ? schema.fallback(dataset, config$1) : schema.fallback;
}
// @__NO_SIDE_EFFECTS__
function getDefault(schema, dataset, config$1) {
  return typeof schema.default === "function" ? schema.default(dataset, config$1) : schema.default;
}
// @__NO_SIDE_EFFECTS__
function boolean(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "boolean",
    reference: boolean,
    expects: "boolean",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "boolean") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function nullable(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "nullable",
    reference: nullable,
    expects: `(${wrapped.expects} | null)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === null) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === null) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
    }
  });
}
// @__NO_SIDE_EFFECTS__
function number(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "number",
    reference: number,
    expects: "number",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "number" && !isNaN(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function object(entries$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "object",
    reference: object,
    expects: "Object",
    async: false,
    entries: entries$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const key in this.entries) {
          const valueSchema = this.entries[key];
          if (key in input || (valueSchema.type === "exact_optional" || valueSchema.type === "optional" || valueSchema.type === "nullish") && valueSchema.default !== void 0) {
            const value$1 = key in input ? input[key] : /* @__PURE__ */ getDefault(valueSchema);
            const valueDataset = valueSchema["~run"]({ value: value$1 }, config$1);
            if (valueDataset.issues) {
              const pathItem = {
                type: "object",
                origin: "value",
                input,
                key,
                value: value$1
              };
              for (const issue of valueDataset.issues) {
                if (issue.path) issue.path.unshift(pathItem);
                else issue.path = [pathItem];
                dataset.issues?.push(issue);
              }
              if (!dataset.issues) dataset.issues = valueDataset.issues;
              if (config$1.abortEarly) {
                dataset.typed = false;
                break;
              }
            }
            if (!valueDataset.typed) dataset.typed = false;
            dataset.value[key] = valueDataset.value;
          } else if (valueSchema.fallback !== void 0) dataset.value[key] = /* @__PURE__ */ getFallback(valueSchema);
          else if (valueSchema.type !== "exact_optional" && valueSchema.type !== "optional" && valueSchema.type !== "nullish") {
            _addIssue(this, "key", dataset, config$1, {
              input: void 0,
              expected: `"${key}"`,
              path: [{
                type: "object",
                origin: "key",
                input,
                key,
                value: input[key]
              }]
            });
            if (config$1.abortEarly) break;
          }
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function optional(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "optional",
    reference: optional,
    expects: `(${wrapped.expects} | undefined)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === void 0) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === void 0) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
    }
  });
}
// @__NO_SIDE_EFFECTS__
function picklist(options, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "picklist",
    reference: picklist,
    expects: /* @__PURE__ */ _joinExpects(options.map(_stringify), "|"),
    async: false,
    options,
    message: message$1,
    "~run"(dataset, config$1) {
      if (this.options.includes(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function record(key, value$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "record",
    reference: record,
    expects: "Object",
    async: false,
    key,
    value: value$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const entryKey in input) if (/* @__PURE__ */ _isValidObjectKey(input, entryKey)) {
          const entryValue = input[entryKey];
          const keyDataset = this.key["~run"]({ value: entryKey }, config$1);
          if (keyDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "key",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of keyDataset.issues) {
              issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = keyDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          const valueDataset = this.value["~run"]({ value: entryValue }, config$1);
          if (valueDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "value",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of valueDataset.issues) {
              if (issue.path) issue.path.unshift(pathItem);
              else issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = valueDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          if (!keyDataset.typed || !valueDataset.typed) dataset.typed = false;
          if (keyDataset.typed) dataset.value[keyDataset.value] = valueDataset.value;
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function string(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "string",
    reference: string,
    expects: "string",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "string") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function unknown() {
  return _standardSchema({
    kind: "schema",
    type: "unknown",
    reference: unknown,
    expects: "unknown",
    async: false,
    "~run"(dataset) {
      dataset.typed = true;
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function pipe(...pipe$1) {
  return _standardSchema({
    ...pipe$1[0],
    pipe: pipe$1,
    "~run"(dataset, config$1) {
      for (const item of pipe$1) if (item.kind !== "metadata") {
        if (dataset.issues && (item.kind === "schema" || item.kind === "transformation")) {
          dataset.typed = false;
          break;
        }
        if (!dataset.issues || !config$1.abortEarly && !config$1.abortPipeEarly) dataset = item["~run"](dataset, config$1);
      }
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function safeParse(schema, input, config$1) {
  const dataset = schema["~run"]({ value: input }, /* @__PURE__ */ getGlobalConfig(config$1));
  return {
    typed: dataset.typed,
    success: !dataset.issues,
    output: dataset.value,
    issues: dataset.issues
  };
}

// web/scripts/schema.ts
var publicErrorSchema = object({
  error: optional(
    pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
  )
});
function parsePublicError(value) {
  const result = safeParse(publicErrorSchema, value);
  if (!result.success) return void 0;
  return result.output.error;
}

// web/scripts/settings/schema.ts
var unknownRecordSchema = record(string(), unknown());
var settingNameSchema = pipe(string(), regex(browserPatterns.settingName));
var settingDefinitionSchema = object({
  minimum: pipe(number(), safeInteger()),
  maximum: pipe(number(), safeInteger())
});
var labelSchema = pipe(string(), minLength(1), maxLength(64));
var signInSchema = object({
  state: picklist(["waiting", "expired", "failed"]),
  user_code: pipe(string(), minLength(1), maxLength(32)),
  verification_url: pipe(string(), url(), startsWith("https://")),
  expires_at: pipe(string(), isoTimestamp()),
  message: nullable(
    pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
  )
});
var configurationDocumentSchema = object({
  revision: pipe(string(), regex(browserPatterns.revision)),
  mutation_allowed: boolean(),
  setting_ranges: unknown(),
  settings: unknownRecordSchema,
  cli: object({
    found: boolean(),
    version: nullable(labelSchema),
    minimum_version: labelSchema,
    is_current: boolean()
  }),
  account: object({
    signed_in: boolean(),
    is_vip: nullable(boolean()),
    vip_level: nullable(labelSchema)
  }),
  sign_in: nullable(signInSchema)
});
function parseDefinitions(value) {
  const document2 = safeParse(unknownRecordSchema, value);
  if (!document2.success) throw new Error(message("settings.invalidResponse"));
  const definitions = /* @__PURE__ */ new Map();
  for (const [name, raw] of Object.entries(document2.output)) {
    const validName = safeParse(settingNameSchema, name);
    const definition = safeParse(settingDefinitionSchema, raw);
    if (!validName.success || !definition.success || definition.output.minimum > definition.output.maximum) {
      throw new Error(message("settings.invalidDefinition"));
    }
    definitions.set(name, definition.output);
  }
  return Object.fromEntries(definitions);
}
function parseSignIn(signIn) {
  if (signIn === null) return void 0;
  return {
    state: signIn.state,
    userCode: signIn.user_code,
    verificationUrl: signIn.verification_url,
    expiresAt: Date.parse(signIn.expires_at),
    message: signIn.message ?? void 0
  };
}
function parseConfiguration(value) {
  const result = safeParse(configurationDocumentSchema, value);
  if (!result.success) throw new Error(message("settings.invalidResponse"));
  const document2 = result.output;
  const definitions = parseDefinitions(document2.setting_ranges);
  const settings = new Map(Object.entries(document2.settings));
  for (const [name, definition] of Object.entries(definitions)) {
    const setting = safeParse(
      pipe(
        number(),
        safeInteger(),
        minValue(definition.minimum),
        maxValue(definition.maximum)
      ),
      settings.get(name)
    );
    if (!setting.success) throw new Error(message("settings.invalidLimit"));
  }
  const { cli, account } = document2;
  return {
    revision: document2.revision,
    mutationAllowed: document2.mutation_allowed,
    definitions,
    settings: document2.settings,
    cli: {
      found: cli.found,
      version: cli.version ?? void 0,
      minimumVersion: cli.minimum_version,
      isCurrent: cli.is_current
    },
    account: { signedIn: account.signed_in, vipLevel: account.vip_level ?? void 0 },
    signIn: parseSignIn(document2.sign_in)
  };
}

// web/scripts/settings/api.ts
var FAILURES = /* @__PURE__ */ new Map([
  [`GET ${browserRoutes.settings.status}`, "settings.readFailed"],
  [`POST ${browserRoutes.settings.session}`, "account.signInFailed"],
  [`DELETE ${browserRoutes.settings.session}`, "account.signOutFailed"],
  [`POST ${browserRoutes.settings.cli}`, "cli.installFailed"]
]);
async function requestConfiguration(fetcher, signal, route = browserRoutes.settings.status, method = "GET", body) {
  const timeout = route === browserRoutes.settings.cli ? browserLimits.installTimeoutMilliseconds : browserLimits.requestTimeoutMilliseconds;
  const options = {
    method,
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([signal, AbortSignal.timeout(timeout)]),
    headers: { "Content-Type": "application/json", "X-Dreamina-Comfy": "1" }
  };
  if (body !== void 0) options.body = JSON.stringify(body);
  let response;
  try {
    response = await fetcher(route, options);
  } catch {
    throw new Error(message("settings.unreachable"));
  }
  let document2;
  try {
    document2 = await response.json();
  } catch {
    throw new Error(message("settings.unreadableResponse"));
  }
  if (!response.ok) {
    throw new Error(
      parsePublicError(document2) ?? message(FAILURES.get(`${method} ${route}`) ?? "settings.saveFailed")
    );
  }
  return parseConfiguration(document2);
}

// web/scripts/settings/dialog.ts
var current;
var SettingsDialog = class {
  /**
   * Build the dialog's parts without contacting the server.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(fetcher) {
    this.fetcher = fetcher;
    this.dialog.className = "dreamina-dialog";
    this.dialog.setAttribute("aria-labelledby", "dreamina-settings-title");
    const heading = element("h2", message("settings.title"));
    heading.id = "dreamina-settings-title";
    const close = button(message("close"));
    close.setAttribute("aria-label", message("settings.close"));
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener("click", () => this.updateSettings(message("settings.reread")));
    const footer = element("footer");
    footer.append(this.status, this.reload);
    this.dialog.append(
      header,
      this.cli.form,
      this.account.form,
      element("p", message("account.notice")),
      this.limits(),
      footer
    );
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
  }
  fetcher;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  status = element("p", message("settings.reading"));
  reload = button(message("settings.reload"));
  limitFields = element("fieldset");
  inputs = /* @__PURE__ */ new Map();
  cli = new CliSection({
    update: (success, route, method, working) => this.updateSettings(success, route, method, void 0, working)
  });
  account = new AccountSection({
    update: (success, route, method) => this.updateSettings(success, route, method),
    poll: () => this.pollStatus(),
    report: (text) => setText(this.status, text)
  });
  configuration;
  // Every request joins this chain, so the next one starts only after the last one settles.
  pending = Promise.resolve();
  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  limits() {
    const form = element("form");
    this.limitFields.disabled = true;
    this.limitFields.append(element("legend", message("settings.limits")));
    this.limitFields.append(button(message("settings.saveLimits"), "submit"));
    form.append(this.limitFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }
  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits.
   */
  populateLimits(configuration) {
    this.limitFields.replaceChildren(element("legend", message("settings.limits")));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const label = element("label", LIMIT_LABELS.get(name) ?? name);
      const input = element("input");
      input.type = "number";
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = "1";
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      this.limitFields.append(label);
    }
    this.limitFields.append(button(message("settings.saveLimits"), "submit"));
  }
  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  saveLimits(configuration) {
    const changes = /* @__PURE__ */ new Map();
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== settings.get(name)) changes.set(name, input.valueAsNumber);
    }
    if (changes.size === 0) {
      setText(this.status, message("settings.noLimitChanges"));
      return;
    }
    this.updateSettings(message("settings.limitsSaved"), browserRoutes.settings.values, "PATCH", {
      revision: configuration.revision,
      settings: Object.fromEntries(changes)
    });
  }
  /**
   * Show the validated status and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  display(configuration) {
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
    if (!configuration.mutationAllowed) setText(this.status, message("settings.readOnly"));
  }
  /**
   * Queue a request after the last one, disabling the parts and showing its working text.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @param working - The text shown while the request runs.
   */
  updateSettings(success, route, method, body, working = message("working")) {
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
  async requestSettings(success, route, method, body) {
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body
      );
      if (this.controller.signal.aborted) return;
      setText(this.status, success);
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message("settings.updateFailed")
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
  pollStatus() {
    const reply = this.pending.then(async () => {
      try {
        const value = await requestConfiguration(this.fetcher, this.controller.signal);
        if (this.controller.signal.aborted) return void 0;
        this.cli.display(value.cli);
        this.account.display(value);
        return value;
      } catch (error) {
        if (!this.controller.signal.aborted)
          setText(
            this.status,
            error instanceof Error ? error.message : message("settings.readFailed")
          );
        return void 0;
      }
    });
    this.pending = reply.then(() => void 0);
    return reply;
  }
  /** Show the dialog and read the status. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateSettings(message("settings.reread"));
  }
  /** Stop requests and the sign-in poll, and return focus to the caller. */
  dispose() {
    this.account.dispose();
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openSettings(fetcher) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new SettingsDialog(fetcher);
  current.show();
}

// web/scripts/extension.ts
app2.registerExtension({
  name: "dreamina",
  setup: () => {
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = new URL("./extension.css", import.meta.url).href;
    const stylesheets = /* @__PURE__ */ new Set();
    for (const link of document.querySelectorAll("link[rel=stylesheet]")) {
      stylesheets.add(link.getAttribute("href"));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
  commands: [
    {
      id: "dreamina.OpenSettings",
      label: message("settings.menu"),
      function: openSettings.bind(null, requestLocal)
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "Dreamina"],
      commands: ["dreamina.OpenSettings"]
    }
  ]
});
