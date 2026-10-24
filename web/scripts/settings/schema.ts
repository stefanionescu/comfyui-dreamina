import * as v from 'valibot';
import { message } from '#web/text.ts';
import { browserLimits, browserPatterns } from '#web/browser.ts';

type SettingDefinition = { minimum: number; maximum: number };

export type CliStatus = {
    found: boolean;
    version: string | undefined;
    minimumVersion: string;
    isCurrent: boolean;
};

type AccountStatus = { signedIn: boolean; vipLevel: string | undefined };

type SignInStatus = {
    state: 'waiting' | 'expired' | 'failed';
    userCode: string;
    verificationUrl: string;
    expiresAt: number;
    message: string | undefined;
};

export type Configuration = {
    revision: string;
    mutationAllowed: boolean;
    definitions: Record<string, SettingDefinition>;
    settings: Record<string, number>;
    cli: CliStatus;
    account: AccountStatus;
    signIn: SignInStatus | undefined;
};

const unknownRecordSchema = v.record(v.string(), v.unknown());

const settingNameSchema = v.pipe(v.string(), v.regex(browserPatterns.settingName));

const settingDefinitionSchema = v.object({
    minimum: v.pipe(v.number(), v.safeInteger()),
    maximum: v.pipe(v.number(), v.safeInteger()),
});

const labelSchema = v.pipe(v.string(), v.minLength(1), v.maxLength(64));

const signInSchema = v.object({
    state: v.picklist(['waiting', 'expired', 'failed']),
    user_code: v.pipe(v.string(), v.minLength(1), v.maxLength(32)),
    verification_url: v.pipe(v.string(), v.url(), v.startsWith('https://')),
    expires_at: v.pipe(v.string(), v.isoTimestamp()),
    message: v.nullable(v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters))),
});

const configurationDocumentSchema = v.object({
    revision: v.pipe(v.string(), v.regex(browserPatterns.revision)),
    mutation_allowed: v.boolean(),
    setting_ranges: v.unknown(),
    settings: unknownRecordSchema,
    cli: v.object({
        found: v.boolean(),
        version: v.nullable(labelSchema),
        minimum_version: labelSchema,
        is_current: v.boolean(),
    }),
    account: v.object({
        signed_in: v.boolean(),
        is_vip: v.nullable(v.boolean()),
        vip_level: v.nullable(labelSchema),
    }),
    sign_in: v.nullable(signInSchema),
});

/**
 * Read the settings fields and ranges supplied by the backend.
 *
 * @param value - The untrusted settings definitions.
 * @returns The validated definitions indexed by setting name.
 */
function parseDefinitions(value: unknown): Configuration['definitions'] {
    const document = v.safeParse(unknownRecordSchema, value);
    if (!document.success) throw new Error(message('settings.invalidResponse'));
    const definitions = new Map<string, SettingDefinition>();
    for (const [name, raw] of Object.entries(document.output)) {
        const validName = v.safeParse(settingNameSchema, name);
        const definition = v.safeParse(settingDefinitionSchema, raw);
        if (!validName.success || !definition.success || definition.output.minimum > definition.output.maximum) {
            throw new Error(message('settings.invalidDefinition'));
        }
        definitions.set(name, definition.output);
    }
    return Object.fromEntries(definitions);
}

/**
 * Read a pending sign-in, keeping its expiry as milliseconds.
 *
 * @param signIn - The validated sign-in, or null when none is pending.
 * @returns The sign-in the account part shows, or undefined.
 */
function parseSignIn(signIn: v.InferOutput<typeof signInSchema> | null): SignInStatus | undefined {
    if (signIn === null) return undefined;
    return {
        state: signIn.state,
        userCode: signIn.user_code,
        verificationUrl: signIn.verification_url,
        expiresAt: Date.parse(signIn.expires_at),
        message: signIn.message ?? undefined,
    };
}

/**
 * Validate and transform the status the local server returns.
 *
 * @param value - The untrusted JSON response.
 * @returns The settings, the CLI, the account, and any pending sign-in.
 */
export function parseConfiguration(value: unknown): Configuration {
    const result = v.safeParse(configurationDocumentSchema, value);
    if (!result.success) throw new Error(message('settings.invalidResponse'));
    const document = result.output;
    const definitions = parseDefinitions(document.setting_ranges);
    const settings = new Map(Object.entries(document.settings));
    for (const [name, definition] of Object.entries(definitions)) {
        const setting = v.safeParse(
            v.pipe(v.number(), v.safeInteger(), v.minValue(definition.minimum), v.maxValue(definition.maximum)),
            settings.get(name),
        );
        if (!setting.success) throw new Error(message('settings.invalidLimit'));
    }
    const { cli, account } = document;
    return {
        revision: document.revision,
        mutationAllowed: document.mutation_allowed,
        definitions,
        settings: document.settings as Configuration['settings'],
        cli: {
            found: cli.found,
            version: cli.version ?? undefined,
            minimumVersion: cli.minimum_version,
            isCurrent: cli.is_current,
        },
        account: { signedIn: account.signed_in, vipLevel: account.vip_level ?? undefined },
        signIn: parseSignIn(document.sign_in),
    };
}
