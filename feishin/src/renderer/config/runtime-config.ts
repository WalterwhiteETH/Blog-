import { ServerType, toServerType } from '/@/shared/types/types';

export interface RuntimeConfig {
    analyticsDisabled: boolean;
    legacyAuthentication: boolean;
    serverLock: boolean;
    serverName: string;
    serverPassword: string;
    serverType: null | ServerType;
    serverUrl: string;
    serverUsername: string;
}

const toBoolean = (value: boolean | string | undefined) => value === true || value === 'true';

export const getRuntimeConfig = (): RuntimeConfig => ({
    analyticsDisabled: toBoolean(window.ANALYTICS_DISABLED),
    legacyAuthentication: toBoolean(window.LEGACY_AUTHENTICATION),
    serverLock: toBoolean(window.SERVER_LOCK),
    serverName: window.SERVER_NAME || 'Music',
    serverPassword: window.SERVER_PASSWORD || '',
    serverType: window.SERVER_TYPE ? toServerType(window.SERVER_TYPE) : null,
    serverUrl: window.SERVER_URL || '',
    serverUsername: window.SERVER_USERNAME || '',
});
