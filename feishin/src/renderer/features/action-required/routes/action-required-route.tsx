import { Navigate } from 'react-router';

import LoginRoute from '/@/renderer/features/login/routes/login-route';
import { useCurrentServerWithCredential } from '/@/renderer/store';

const ActionRequiredRoute = () => {
    const currentServer = useCurrentServerWithCredential();

    if (currentServer?.credential) {
        return <Navigate replace to="/" />;
    }

    return <LoginRoute />;
};

export default ActionRequiredRoute;
