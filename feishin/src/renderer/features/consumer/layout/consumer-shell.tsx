import clsx from 'clsx';
import { MdMusicNote } from 'react-icons/md';
import { NavLink, Outlet, useLocation } from 'react-router';

import styles from './consumer-shell.module.css';

import { ConsumerPlayerDock } from '/@/renderer/features/consumer/components';
import { consumerNavigationItems } from '/@/renderer/features/consumer/constants';
import { AppRoute } from '/@/renderer/router/routes';

export const ConsumerShell = () => {
    const location = useLocation();
    const isNowPlaying = location.pathname === AppRoute.NOW_PLAYING;

    return (
        <div className={clsx(styles.shell, isNowPlaying && styles.shellNowPlaying)}>
            <aside className={styles.sidebar}>
                <div className={styles.brand}>
                    <div className={styles.brandMark}>
                        <MdMusicNote aria-hidden />
                    </div>
                    <div>
                        <div className={styles.brandTitle}>Music</div>
                        <div className={styles.brandSubtitle}>Listen now</div>
                    </div>
                </div>
                <nav className={styles.nav}>
                    {consumerNavigationItems.map((item) => (
                        <NavLink
                            className={({ isActive }) =>
                                clsx(styles.navItem, isActive && styles.navItemActive)
                            }
                            end={item.to === AppRoute.HOME}
                            key={item.to}
                            to={item.to}
                        >
                            <item.icon aria-hidden className={styles.navIcon} />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>
            </aside>

            <main className={clsx(styles.content, isNowPlaying && styles.contentNowPlaying)}>
                <Outlet />
            </main>

            {!isNowPlaying && <ConsumerPlayerDock />}

            {!isNowPlaying && (
                <nav className={styles.bottomNav}>
                    {consumerNavigationItems.map((item) => (
                        <NavLink
                            className={({ isActive }) =>
                                clsx(styles.bottomNavItem, isActive && styles.bottomNavItemActive)
                            }
                            end={item.to === AppRoute.HOME}
                            key={item.to}
                            to={item.to}
                        >
                            <item.icon aria-hidden className={styles.bottomNavIcon} />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>
            )}
        </div>
    );
};
