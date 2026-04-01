import formatDuration from 'format-duration';
import { useMemo } from 'react';
import {
    MdKeyboardArrowDown,
    MdMusicNote,
    MdPause,
    MdPlayArrow,
    MdSkipNext,
    MdSkipPrevious,
    MdVolumeUp,
} from 'react-icons/md';
import { useNavigate } from 'react-router';

import styles from './consumer-screens.module.css';

import { useItemImageUrl } from '/@/renderer/components/item-image/item-image';
import { usePlayer } from '/@/renderer/features/player/context/player-context';
import { AppRoute } from '/@/renderer/router/routes';
import {
    usePlayerSong,
    usePlayerStatus,
    usePlayerTimestamp,
    usePlayerVolume,
} from '/@/renderer/store';
import { LibraryItem } from '/@/shared/types/domain-types';
import { PlayerStatus } from '/@/shared/types/types';

export default function NowPlayingScreen() {
    const navigate = useNavigate();
    const player = usePlayer();
    const currentSong = usePlayerSong();
    const status = usePlayerStatus();
    const timestamp = usePlayerTimestamp();
    const volume = usePlayerVolume();

    const coverUrl = useItemImageUrl({
        id: currentSong?.imageId,
        itemType: LibraryItem.SONG,
        serverId: currentSong?._serverId,
        type: 'itemCard',
    });

    const duration = currentSong?.duration ? currentSong.duration / 1000 : 0;
    const currentTime = Math.min(duration, timestamp);
    const totalLabel = useMemo(() => formatDuration(duration * 1000), [duration]);
    const elapsedLabel = useMemo(() => formatDuration(currentTime * 1000), [currentTime]);

    return (
        <div className={styles.playerScreen}>
            <div className={styles.playerTopBar}>
                <button
                    aria-label="Close now playing"
                    className={styles.playerTopButton}
                    onClick={() => {
                        if (window.history.length > 1) {
                            navigate(-1);
                            return;
                        }

                        navigate(AppRoute.HOME);
                    }}
                    type="button"
                >
                    <MdKeyboardArrowDown aria-hidden />
                </button>
                <div className={styles.playerTopCopy}>
                    <div className={styles.eyebrow}>Now playing</div>
                    <div className={styles.playerTopTitle}>Playing from your library</div>
                </div>
            </div>

            <div className={styles.playerHero}>
                <div className={styles.playerArt}>
                    {coverUrl ? (
                        <img alt={currentSong?.name || 'Album art'} src={coverUrl} />
                    ) : (
                        <MdMusicNote aria-hidden />
                    )}
                </div>
                <div className={styles.playerCopy}>
                    <h1>{currentSong?.name || 'Choose something to play'}</h1>
                    <p>
                        {currentSong?.artistName ||
                            currentSong?.albumArtistName ||
                            'Your next favorite track is waiting.'}
                    </p>
                </div>
            </div>

            <div className={styles.playerPanel}>
                <div className={styles.progressRow}>
                    <span>{elapsedLabel}</span>
                    <input
                        aria-label="Playback progress"
                        max={duration || 0}
                        min={0}
                        onChange={(event) =>
                            player.mediaSeekToTimestamp(Number(event.currentTarget.value))
                        }
                        type="range"
                        value={currentTime}
                    />
                    <span>{totalLabel}</span>
                </div>

                <div className={styles.transportRow}>
                    <button
                        aria-label="Previous"
                        onClick={() => player.mediaPrevious()}
                        type="button"
                    >
                        <MdSkipPrevious aria-hidden />
                    </button>
                    <button
                        aria-label={status === PlayerStatus.PLAYING ? 'Pause' : 'Play'}
                        className={styles.transportPrimary}
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

                <div className={styles.volumeRow}>
                    <span>
                        <MdVolumeUp aria-hidden />
                    </span>
                    <input
                        aria-label="Volume"
                        max={100}
                        min={0}
                        onChange={(event) => player.setVolume(Number(event.currentTarget.value))}
                        type="range"
                        value={volume}
                    />
                </div>
            </div>
        </div>
    );
}
