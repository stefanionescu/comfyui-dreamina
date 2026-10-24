/** Request deadlines, the sign-in poll, and response size limits for the interface. */
export const browserLimits = {
    requestTimeoutMilliseconds: 60_000,
    installTimeoutMilliseconds: 390_000,
    signInPollMilliseconds: 2000,
    maxErrorCharacters: 1024,
} as const;

/** Formats accepted from the local ComfyUI API. */
export const browserPatterns = {
    revision: /^[a-f0-9]{64}$/,
    settingName: /^[a-z][a-z_]+$/,
} as const;
