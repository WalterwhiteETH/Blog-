import { IconType } from 'react-icons';
import { MdHomeFilled, MdLibraryMusic, MdSearch } from 'react-icons/md';

import { AppRoute } from '/@/renderer/router/routes';

export interface ConsumerNavigationItem {
    icon: IconType;
    label: string;
    to: AppRoute;
}

export const consumerNavigationItems: ConsumerNavigationItem[] = [
    {
        icon: MdHomeFilled,
        label: 'Home',
        to: AppRoute.HOME,
    },
    {
        icon: MdSearch,
        label: 'Search',
        to: AppRoute.SEARCH,
    },
    {
        icon: MdLibraryMusic,
        label: 'Library',
        to: AppRoute.LIBRARY,
    },
];
