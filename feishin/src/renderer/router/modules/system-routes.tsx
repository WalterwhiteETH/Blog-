import { lazy } from 'react';
import { Route } from 'react-router';

import { AppRoute } from '/@/renderer/router/routes';
import { TitlebarOutlet } from '/@/renderer/router/titlebar-outlet';

const ActionRequiredRoute = lazy(
    () => import('/@/renderer/features/action-required/routes/action-required-route'),
);
const LoginRoute = lazy(() => import('/@/renderer/features/login/routes/login-route'));
const NoNetworkRoute = lazy(
    () => import('/@/renderer/features/action-required/routes/no-network-route'),
);

export const systemRoutes = (
    <Route element={<TitlebarOutlet />}>
        <Route element={<ActionRequiredRoute />} path={AppRoute.ACTION_REQUIRED} />
        <Route element={<LoginRoute />} path={AppRoute.LOGIN} />
        <Route element={<NoNetworkRoute />} path={AppRoute.NO_NETWORK} />
    </Route>
);
