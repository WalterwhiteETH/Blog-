import { Suspense } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router';

import { RouterErrorBoundary } from '/@/renderer/features/shared/components/router-error-boundary';
import { AuthenticationOutlet } from '/@/renderer/layouts/authentication-outlet';
import { AppOutlet } from '/@/renderer/router/app-outlet';
import { consumerRoutes } from '/@/renderer/router/modules/consumer-routes';
import { modalRegistry } from '/@/renderer/router/modules/modal-registry';
import { systemRoutes } from '/@/renderer/router/modules/system-routes';
import { TitlebarOutlet } from '/@/renderer/router/titlebar-outlet';
import { BaseContextModal, ModalsProvider } from '/@/shared/components/modal/modal';

export const AppRouter = () => {
    const router = (
        <MemoryRouter initialEntries={['/']}>
            <ModalsProvider
                modals={{
                    ...modalRegistry,
                    base: BaseContextModal,
                }}
            >
                <RouterErrorBoundary>
                    <Routes>
                        <Route element={<AuthenticationOutlet />}>
                            <Route element={<TitlebarOutlet />}>
                                <Route element={<AppOutlet />}>{consumerRoutes}</Route>
                            </Route>
                        </Route>
                        {systemRoutes}
                    </Routes>
                </RouterErrorBoundary>
            </ModalsProvider>
        </MemoryRouter>
    );

    return <Suspense fallback={<></>}>{router}</Suspense>;
};
