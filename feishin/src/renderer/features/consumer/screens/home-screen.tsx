import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { useNavigate } from 'react-router';

import styles from './consumer-screens.module.css';

import { albumQueries } from '/@/renderer/features/albums/api/album-api';
import { MediaCard } from '/@/renderer/features/consumer/components';
import { homeQueries } from '/@/renderer/features/home/api/home-api';
import { usePlayer } from '/@/renderer/features/player/context/player-context';
import { AppRoute } from '/@/renderer/router/routes';
import { useCurrentServerId } from '/@/renderer/store';
import { AlbumListSort, LibraryItem, SortOrder } from '/@/shared/types/domain-types';
import { Play } from '/@/shared/types/types';

export default function HomeScreen() {
    const navigate = useNavigate();
    const player = usePlayer();
    const serverId = useCurrentServerId();

    const recentlyPlayed = useQuery(
        homeQueries.recentlyPlayed({
            options: {
                enabled: Boolean(serverId),
            },
            query: { limit: 10 },
            serverId,
        }),
    );

    const madeForYou = useQuery(
        albumQueries.list({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 10,
                sortBy: AlbumListSort.RANDOM,
                sortOrder: SortOrder.ASC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const trending = useQuery(
        albumQueries.list({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 10,
                sortBy: AlbumListSort.PLAY_COUNT,
                sortOrder: SortOrder.DESC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const greeting = useMemo(() => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 18) return 'Good afternoon';
        return 'Good evening';
    }, []);

    const playAlbum = (albumId: string) => {
        if (!serverId) return;
        player.addToQueueByFetch(serverId, [albumId], LibraryItem.ALBUM, Play.NOW);
        navigate(AppRoute.NOW_PLAYING);
    };

    return (
        <div className={styles.screen}>
            <div className={styles.hero}>
                <div>
                    <div className={styles.eyebrow}>For you</div>
                    <h1>{greeting}</h1>
                    <p>Your music, simplified. Jump back in or find something new.</p>
                </div>
                <button
                    className={styles.searchShortcut}
                    onClick={() => navigate(AppRoute.SEARCH)}
                    type="button"
                >
                    Search music
                </button>
            </div>

            <SectionRow
                items={recentlyPlayed.data?.items ?? []}
                onSelect={playAlbum}
                title="Recently Played"
            />
            <SectionRow
                items={madeForYou.data?.items ?? []}
                onSelect={playAlbum}
                title="Made For You"
            />
            <SectionRow items={trending.data?.items ?? []} onSelect={playAlbum} title="Trending" />
        </div>
    );
}

function SectionRow({
    items,
    onSelect,
    title,
}: {
    items: Array<{
        _serverId: string;
        albumArtistName: string;
        id: string;
        imageId: null | string;
        name: string;
    }>;
    onSelect: (id: string) => void;
    title: string;
}) {
    return (
        <section className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>{title}</h2>
            </div>
            <div className={styles.horizontalRail}>
                {items.map((item) => (
                    <button
                        className={styles.cardButton}
                        key={item.id}
                        onClick={() => onSelect(item.id)}
                        type="button"
                    >
                        <MediaCard
                            artist={item.albumArtistName || 'Unknown artist'}
                            imageId={item.imageId}
                            serverId={item._serverId}
                            title={item.name}
                            type={LibraryItem.ALBUM}
                        />
                    </button>
                ))}
            </div>
        </section>
    );
}
