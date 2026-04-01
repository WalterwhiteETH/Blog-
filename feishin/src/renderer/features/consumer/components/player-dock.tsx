import clsx from 'clsx';
import {
    MdMusicNote,
    MdPause,
    MdPlayArrow,
    MdRepeat,
    MdSkipNext,
    MdSkipPrevious,
    MdVolumeUp,
} from 'react-icons/md';
import { useNavigate } from 'react-router';

import { useItemImageUrl } from '/@/renderer/components/item-image/item-image';
import styles from '/@/renderer/features/consumer/layout/consumer-shell.module.css';
import { usePlayer } from '/@/renderer/features/player/context/player-context';
import { AppRoute } from '/@/renderer/router/routes';
import {
    usePlayerSong,
    usePlayerStatus,
    usePlayerTimestamp,
    usePlayerVolume,
} from '/@/renderer/store';
import { LibraryItem } from '/@/shared/types/domain-types';
import { Play, PlayerStatus } from '/@/shared/types/types';

export const ConsumerPlayerDock = () => {
    const navigate = useNavigate();
    const player = usePlayer();
    const currentSong = usePlayerSong();
    const status = usePlayerStatus();
    const timestamp = usePlayerTimestamp();
    const volume = usePlayerVolume();
    const progress = currentSong?.duration
        ? Math.min(100, (timestamp / (currentSong.duration / 1000)) * 100)
        : 0;

    const coverUrl = useItemImageUrl({
        id: currentSong?.imageId,
        itemType: LibraryItem.SONG,
        serverId: currentSong?._serverId,
        type: 'table',
    });

    if (!currentSong) {
        return (
            <div className={clsx(styles.playerDock, styles.playerDockIdle)}>
                <div>
                    <div className={styles.playerDockLabel}>Nothing playing</div>
                    <div className={styles.playerDockMeta}>Pick an album, artist, or playlist</div>
                </div>
            </div>
        );
    }

    return (
        <div
            className={styles.playerDock}
            onClick={() => navigate(AppRoute.NOW_PLAYING)}
            onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    navigate(AppRoute.NOW_PLAYING);
                }
            }}
            role="button"
            tabIndex={0}
        >
            <div className={styles.playerDockProgress} style={{ width: `${progress}%` }} />
            <div className={styles.playerDockMedia}>
                <div className={styles.playerDockArt}>
                    {coverUrl ? (
                        <img alt={currentSong.name} src={coverUrl} />
                    ) : (
                        <MdMusicNote aria-hidden />
                    )}
                </div>
                <div className={styles.playerDockText}>
                    <div className={styles.playerDockTitle}>{currentSong.name}</div>
                    <div className={styles.playerDockMeta}>
                        {currentSong.artistName || currentSong.albumArtistName || 'Unknown artist'}
                    </div>
                </div>
            </div>

            <div
                className={styles.playerDockControls}
                onClick={(event) => event.stopPropagation()}
                onMouseDown={(event) => event.stopPropagation()}
            >
                <button aria-label="Previous" onClick={() => player.mediaPrevious()} type="button">
                    <MdSkipPrevious aria-hidden />
                </button>
                <button
                    aria-label={status === PlayerStatus.PLAYING ? 'Pause' : 'Play'}
                    className={styles.playerDockPrimary}
                    onClick={() => player.mediaTogglePlayPause()}
                    type="button"
                >
                    {status === PlayerStatus.PLAYING ? (
                        <MdPause aria-hidden />
                    ) : (
                        <MdPlayArrow aria-hidden />
                    )}
                </button>
                <button aria-label="Next" onClick={() => player.mediaNext()} type="button">
                    <MdSkipNext aria-hidden />
                </button>
            </div>

            <div
                className={styles.playerDockActions}
                onClick={(event) => event.stopPropagation()}
                onMouseDown={(event) => event.stopPropagation()}
            >
                <MdVolumeUp aria-hidden className={styles.volumeIcon} />
                <input
                    aria-label="Volume"
                    max={100}
                    min={0}
                    onChange={(event) => player.setVolume(Number(event.currentTarget.value))}
                    type="range"
                    value={volume}
                />
                <button
                    aria-label="Replay"
                    className={styles.playerDockQueue}
                    onClick={() => player.addToQueueByData([currentSong], Play.NOW, currentSong.id)}
                    type="button"
                >
                    <MdRepeat aria-hidden />
                </button>
            </div>
        </div>
    );
};
