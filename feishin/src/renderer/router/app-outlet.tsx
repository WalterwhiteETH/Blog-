import { useMemo } from 'react';
import { Navigate, Outlet } from 'react-router';

import { getRuntimeConfig } from '/@/renderer/config/runtime-config';
import { isServerLock } from '/@/renderer/features/action-required/utils/window-properties';
import { AppRoute } from '/@/renderer/router/routes';
import { useAuthStoreActions, useCurrentServer } from '/@/renderer/store';

const normalizeUrl = (url: string) => url.replace(/\/$/, '');

export const AppOutlet = () => {
    const currentServer = useCurrentServer();
    const { deleteServer, setCurrentServer } = useAuthStoreActions();
    const runtimeConfig = getRuntimeConfig();

    const isActionsRequired = useMemo(() => {
        // When SERVER_LOCK is enabled and the configured URL has changed,
        // clear the stale session so the user re-authenticates against the new server.
        if (isServerLock() && currentServer && runtimeConfig.serverUrl) {
            const configuredUrl = normalizeUrl(runtimeConfig.serverUrl);
            const persistedUrl = normalizeUrl(currentServer.url);

            if (configuredUrl !== persistedUrl) {
                deleteServer(currentServer.id);
                setCurrentServer(null);
                return true;
            }
        }

        const isServerRequired = !currentServer;

        const actions = [isServerRequired];
        const isActionRequired = actions.some((c) => c);

        return isActionRequired;
    }, [currentServer, deleteServer, runtimeConfig.serverUrl, setCurrentServer]);

    if (isActionsRequired) {
        return <Navigate replace to={AppRoute.ACTION_REQUIRED} />;
    }

    return <Outlet />;
};
