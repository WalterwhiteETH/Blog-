export interface TelegramWebApp {
    initDataUnsafe?: {
        user?: {
            id?: number;
        };
    };
}

interface TelegramWindow {
    Telegram?: {
        WebApp?: TelegramWebApp;
    };
}

export const getTelegramWebApp = (): TelegramWebApp | undefined => {
    return (window as TelegramWindow).Telegram?.WebApp;
};

export const isTelegramMiniApp = (): boolean => {
    return Boolean(getTelegramWebApp());
};

export const getTelegramUserId = (): null | string => {
    const id = getTelegramWebApp()?.initDataUnsafe?.user?.id;
    return id ? String(id) : null;
};
