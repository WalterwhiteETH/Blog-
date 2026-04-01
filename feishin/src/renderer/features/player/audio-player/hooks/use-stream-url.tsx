import { openModal } from '@mantine/modals';
import { useEffect, useMemo, useRef, useState } from 'react';

import { api } from '/@/renderer/api';
import { checkSubscription } from '/@/renderer/api/client';
import { useCurrentServer } from '/@/renderer/store';
import { TranscodingConfig } from '/@/renderer/store';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';
import { QueueSong } from '/@/shared/types/domain-types';

const isPremiumTrack = (song: QueueSong) => {
    const premiumTags = song.tags?.premium || song.tags?.Premium;
    if (premiumTags && premiumTags.length > 0) {
        return premiumTags.some((value) => String(value).toLowerCase() === 'true');
    }
    return song.name.toLowerCase().includes('[premium]');
};

export function useSongUrl(
    song: QueueSong | undefined,
    current: boolean,
    transcode: TranscodingConfig,
): string | undefined {
    const prior = useRef(['', '']);
    const currentServer = useCurrentServer();
    const [allowedToPlay, setAllowedToPlay] = useState(true);

    useEffect(() => {
        let mounted = true;

        const validateSubscription = async () => {
            if (!song || !isPremiumTrack(song)) {
                if (mounted) setAllowedToPlay(true);
                return;
            }

            try {
                const userId = currentServer?.userId || '1';
                const result = await checkSubscription(userId);
                const subscribed = Boolean(result?.subscribed);

                if (!subscribed) {
                    openModal({
                        children: <Text>Subscribe to play this song</Text>,
                        title: 'Subscription Required',
                    });
                    toast.warn({
                        message: 'subscription expired',
                        title: 'Playback',
                    });
                }
                if (mounted) setAllowedToPlay(subscribed);
            } catch (error: unknown) {
                toast.error({
                    message: error instanceof Error ? error.message : 'network error',
                    title: 'Playback',
                });
                if (mounted) setAllowedToPlay(false);
            }
        };

        validateSubscription();
        return () => {
            mounted = false;
        };
    }, [currentServer?.userId, song, song?._uniqueId, song?.name]);

    return useMemo(() => {
        if (!allowedToPlay) {
            return undefined;
        }

        if (song?._serverId) {
            // If we are the current track, we do not want a transcoding
            // reconfiguration to force a restart.
            if (current && prior.current[0] === song._uniqueId) {
                return prior.current[1];
            }

            const url = api.controller.getStreamUrl({
                apiClientProps: { serverId: song._serverId },
                query: {
                    bitrate: transcode.bitrate,
                    format: transcode.format,
                    id: song.id,
                    transcode: transcode.enabled,
                },
            });

            // transcoding enabled; save the updated result
            prior.current = [song._uniqueId, url];
            return url;
        }

        // no track; clear result
        prior.current = ['', ''];
        return undefined;
    }, [
        allowedToPlay,
        song?._serverId,
        song?._uniqueId,
        song?.id,
        current,
        transcode.bitrate,
        transcode.format,
        transcode.enabled,
    ]);
}

export const getSongUrl = (song: QueueSong, transcode: TranscodingConfig) => {
    return api.controller.getStreamUrl({
        apiClientProps: { serverId: song._serverId },
        query: {
            bitrate: transcode.bitrate,
            format: transcode.format,
            id: song.id,
            transcode: transcode.enabled,
        },
    });
};
