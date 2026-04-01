import { getRuntimeConfig } from '/@/renderer/config/runtime-config';

export const isLegacyAuth = () => getRuntimeConfig().legacyAuthentication;

export const isServerLock = () => getRuntimeConfig().serverLock;
