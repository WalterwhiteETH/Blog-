import { useEffect, useRef, useState } from 'react';

import { ItemListHandle } from '/@/renderer/components/item-list/types';
import { NowPlayingHeader } from '/@/renderer/features/now-playing/components/now-playing-header';
import { PlayQueue } from '/@/renderer/features/now-playing/components/play-queue';
import { PlayQueueListControls } from '/@/renderer/features/now-playing/components/play-queue-list-controls';
import { AnimatedPage } from '/@/renderer/features/shared/components/animated-page';
import { PageErrorBoundary } from '/@/renderer/features/shared/components/page-error-boundary';
import { useIsMobile } from '/@/renderer/hooks/use-is-mobile';
import { useAppStoreActions, useSetFullScreenPlayerStore } from '/@/renderer/store';
import { ItemListKey } from '/@/shared/types/types';

const NowPlayingRoute = () => {
    const [search, setSearch] = useState<string | undefined>(undefined);
    const { setSideBar } = useAppStoreActions();
    const setFullScreenPlayerStore = useSetFullScreenPlayerStore();
    const isMobile = useIsMobile();
    const tableRef = useRef<ItemListHandle | null>(null);

    useEffect(() => {
        // On page enter, set rightExpanded to false
        setSideBar({ rightExpanded: false });

        return () => {
            // On page exit, set rightExpanded to true
            setSideBar({ rightExpanded: true });
        };
    }, [setSideBar]);

    useEffect(() => {
        if (!isMobile) {
            return;
        }

        // Mobile default experience should open on the player view.
        setFullScreenPlayerStore({ activeTab: 'player', expanded: true });
    }, [isMobile, setFullScreenPlayerStore]);

    return (
        <AnimatedPage>
            <NowPlayingHeader />
            <PlayQueueListControls
                handleSearch={setSearch}
                searchTerm={search}
                tableRef={tableRef}
                type={ItemListKey.QUEUE_SONG}
            />
            <PlayQueue listKey={ItemListKey.QUEUE_SONG} ref={tableRef} searchTerm={search} />
        </AnimatedPage>
    );
};

const NowPlayingRouteWithBoundary = () => {
    return (
        <PageErrorBoundary>
            <NowPlayingRoute />
        </PageErrorBoundary>
    );
};

export default NowPlayingRouteWithBoundary;
