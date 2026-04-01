import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router';

import styles from './consumer-screens.module.css';

import { MediaCard } from '/@/renderer/features/consumer/components';
import { genresQueries } from '/@/renderer/features/genres/api/genres-api';
import { usePlayer } from '/@/renderer/features/player/context/player-context';
import { searchQueries } from '/@/renderer/features/search/api/search-api';
import { AppRoute } from '/@/renderer/router/routes';
import { useCurrentServerId } from '/@/renderer/store';
import { GenreListSort, LibraryItem, SortOrder } from '/@/shared/types/domain-types';
import { Play } from '/@/shared/types/types';

const genreColors = ['#e13300', '#5038a0', '#148a08', '#bc5900', '#7d4b32', '#2d46b9'];

export default function SearchScreen() {
    const navigate = useNavigate();
    const player = usePlayer();
    const serverId = useCurrentServerId();
    const [query, setQuery] = useState('');

    const genres = useQuery(
        genresQueries.list({
            options: {
                enabled: Boolean(serverId),
            },
            query: {
                limit: 12,
                sortBy: GenreListSort.NAME,
                sortOrder: SortOrder.ASC,
                startIndex: 0,
            },
            serverId,
        }),
    );

    const search = useQuery(
        searchQueries.search({
            options: {
                enabled: Boolean(serverId) && query.trim().length > 0,
            },
            query: {
                albumArtistLimit: 6,
                albumLimit: 6,
                query: query.trim(),
                songLimit: 8,
            },
            serverId,
        }),
    );

    const genreCards = useMemo(
        () =>
            (genres.data?.items ?? []).map((genre, index) => ({
                color: genreColors[index % genreColors.length],
                genre,
            })),
        [genres.data?.items],
    );

    return (
        <div className={styles.screen}>
            <div className={styles.topBar}>
                <h1>Search</h1>
                <input
                    className={styles.searchInput}
                    onChange={(event) => setQuery(event.currentTarget.value)}
                    placeholder="What do you want to hear?"
                    value={query}
                />
            </div>

            {query.trim() ? (
                <div className={styles.searchResults}>
                    <SearchSection
                        items={search.data?.songs ?? []}
                        onSelect={(songId) => {
                            const song = search.data?.songs.find((item) => item.id === songId);
                            if (!song) return;
                            player.addToQueueByData([song], Play.NOW, song.id);
                            navigate(AppRoute.NOW_PLAYING);
                        }}
                        title="Songs"
                        type={LibraryItem.SONG}
                    />
                    <SearchSection
                        items={search.data?.albums ?? []}
                        onSelect={(albumId) => {
                            if (!serverId) return;
                            player.addToQueueByFetch(
                                serverId,
                                [albumId],
                                LibraryItem.ALBUM,
                                Play.NOW,
                            );
                            navigate(AppRoute.NOW_PLAYING);
                        }}
                        title="Albums"
                        type={LibraryItem.ALBUM}
                    />
                    <SearchSection
                        items={search.data?.albumArtists ?? []}
                        onSelect={(artistId) => {
                            if (!serverId) return;
                            player.addToQueueByFetch(
                                serverId,
                                [artistId],
                                LibraryItem.ALBUM_ARTIST,
                                Play.NOW,
                            );
                            navigate(AppRoute.NOW_PLAYING);
                        }}
                        title="Artists"
                        type={LibraryItem.ALBUM_ARTIST}
                    />
                </div>
            ) : (
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2>Browse all</h2>
                    </div>
                    <div className={styles.genreGrid}>
                        {genreCards.map(({ color, genre }) => (
                            <button
                                className={styles.genreCard}
                                key={genre.id}
                                onClick={() => setQuery(genre.name)}
                                style={{ background: `linear-gradient(135deg, ${color}, #181818)` }}
                                type="button"
                            >
                                <span>{genre.name}</span>
                            </button>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}

function SearchSection({
    items,
    onSelect,
    title,
    type,
}: {
    items: Array<{
        _serverId: string;
        albumArtistName?: string;
        artistName?: string;
        id: string;
        imageId: null | string;
        name: string;
    }>;
    onSelect: (id: string) => void;
    title: string;
    type: LibraryItem;
}) {
    if (!items.length) return null;

    return (
        <section className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>{title}</h2>
            </div>
            <div className={styles.searchGrid}>
                {items.map((item) => (
                    <button
                        className={styles.cardButton}
                        key={item.id}
                        onClick={() => onSelect(item.id)}
                        type="button"
                    >
                        <MediaCard
                            artist={item.artistName || item.albumArtistName || 'Unknown artist'}
                            imageId={item.imageId}
                            serverId={item._serverId}
                            title={item.name}
                            type={type}
                        />
                    </button>
                ))}
            </div>
        </section>
    );
}
