import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router';

import styles from './consumer-screens.module.css';

import { albumQueries } from '/@/renderer/features/albums/api/album-api';
import { artistsQueries } from '/@/renderer/features/artists/api/artists-api';
import { LibraryListItem } from '/@/renderer/features/consumer/components';
import { usePlayer } from '/@/renderer/features/player/context/player-context';
import { playlistsQueries } from '/@/renderer/features/playlists/api/playlists-api';
import { AppRoute } from '/@/renderer/router/routes';
import { useCurrentServerId } from '/@/renderer/store';
import {
    AlbumArtistListSort,
    AlbumListSort,
    LibraryItem,
    PlaylistListSort,
    SortOrder,
} from '/@/shared/types/domain-types';
import { Play } from '/@/shared/types/types';

type LibraryTab = 'albums' | 'artists' | 'playlists';

const tabs: LibraryTab[] = ['playlists', 'artists', 'albums'];

export default function LibraryScreen() {
    const navigate = useNavigate();
    const player = usePlayer();
    const serverId = useCurrentServerId();
    const [tab, setTab] = useState<LibraryTab>('playlists');

    const playlists = useQuery(
        playlistsQueries.list({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 20,
                sortBy: PlaylistListSort.UPDATED_AT,
                sortOrder: SortOrder.DESC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const artists = useQuery(
        artistsQueries.albumArtistList({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 20,
                sortBy: AlbumArtistListSort.PLAY_COUNT,
                sortOrder: SortOrder.DESC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const albums = useQuery(
        albumQueries.list({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 20,
                sortBy: AlbumListSort.RECENTLY_ADDED,
                sortOrder: SortOrder.DESC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const renderedItems = useMemo(() => {
        if (tab === 'playlists') {
            return (playlists.data?.items ?? []).map((item) => (
                <button
                    className={styles.listButton}
                    key={item.id}
                    onClick={() => {
                        if (!serverId) return;
                        player.addToQueueByFetch(
                            serverId,
                            [item.id],
                            LibraryItem.PLAYLIST,
                            Play.NOW,
                        );
                        navigate(AppRoute.NOW_PLAYING);
                    }}
                    type="button"
                >
                    <LibraryListItem
                        caption={`${item.songCount ?? 0} songs`}
                        imageId={item.imageId}
                        meta={item.owner || 'Playlist'}
                        serverId={item._serverId}
                        title={item.name}
                        type={LibraryItem.PLAYLIST}
                    />
                </button>
            ));
        }

        if (tab === 'artists') {
            return (artists.data?.items ?? []).map((item) => (
                <button
                    className={styles.listButton}
                    key={item.id}
                    onClick={() => {
                        if (!serverId) return;
                        player.addToQueueByFetch(
                            serverId,
                            [item.id],
                            LibraryItem.ALBUM_ARTIST,
                            Play.NOW,
                        );
                        navigate(AppRoute.NOW_PLAYING);
                    }}
                    type="button"
                >
                    <LibraryListItem
                        caption={`${item.albumCount ?? 0} releases`}
                        imageId={item.imageId}
                        meta="Artist"
                        serverId={item._serverId}
                        title={item.name}
                        type={LibraryItem.ALBUM_ARTIST}
                    />
                </button>
            ));
        }

        return (albums.data?.items ?? []).map((item) => (
            <button
                className={styles.listButton}
                key={item.id}
                onClick={() => {
                    if (!serverId) return;
                    player.addToQueueByFetch(serverId, [item.id], LibraryItem.ALBUM, Play.NOW);
                    navigate(AppRoute.NOW_PLAYING);
                }}
                type="button"
            >
                <LibraryListItem
                    caption={`${item.songCount ?? 0} songs`}
                    imageId={item.imageId}
                    meta={item.albumArtistName || 'Album'}
                    serverId={item._serverId}
                    title={item.name}
                    type={LibraryItem.ALBUM}
                />
            </button>
        ));
    }, [
        albums.data?.items,
        artists.data?.items,
        navigate,
        player,
        playlists.data?.items,
        serverId,
        tab,
    ]);

    return (
        <div className={styles.screen}>
            <div className={styles.topBar}>
                <h1>Your Library</h1>
            </div>

            <div className={styles.tabRow}>
                {tabs.map((tabName) => (
                    <button
                        className={tab === tabName ? styles.tabActive : styles.tab}
                        key={tabName}
                        onClick={() => setTab(tabName)}
                        type="button"
                    >
                        {tabName[0].toUpperCase() + tabName.slice(1)}
                    </button>
                ))}
            </div>

            <div className={styles.listStack}>{renderedItems}</div>
        </div>
    );
}
