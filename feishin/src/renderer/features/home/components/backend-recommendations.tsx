import { useEffect, useState } from 'react';

import { getRecommendations, type RecommendationPayload } from '/@/renderer/api/client';
import { useCurrentServer } from '/@/renderer/store';
import { Stack } from '/@/shared/components/stack/stack';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';

interface RecommendationItem {
    name?: string;
    song?: string;
    title?: string;
}

const RecommendationBlock = ({ items, title }: { items?: RecommendationItem[]; title: string }) => {
    if (!items || items.length === 0) {
        return null;
    }

    return (
        <Stack
            className="telegram-panel"
            gap="xs"
            p="md"
            style={{
                background: 'var(--theme-colors-surface)',
                borderRadius: 12,
            }}
        >
            <Text fw={600}>{title}</Text>
            {items.slice(0, 8).map((item, index) => {
                const label = item?.title || item?.name || item?.song || JSON.stringify(item);
                return (
                    <Text
                        key={`${title}-${index}`}
                        px="sm"
                        py="0.35rem"
                        style={{
                            background:
                                'color-mix(in srgb, var(--theme-colors-background) 70%, transparent)',
                            borderRadius: 10,
                        }}
                        variant="secondary"
                    >
                        {label}
                    </Text>
                );
            })}
        </Stack>
    );
};

export const BackendRecommendations = () => {
    const currentServer = useCurrentServer();
    const userId = currentServer?.userId || '1';
    const [feed, setFeed] = useState<null | RecommendationPayload>(null);

    useEffect(() => {
        let mounted = true;

        const load = async () => {
            try {
                const data = await getRecommendations(userId);
                if (mounted) {
                    setFeed(data);
                }
            } catch (error: unknown) {
                toast.error({
                    message: error instanceof Error ? error.message : 'network error',
                    title: 'Recommendations',
                });
            }
        };

        load();

        return () => {
            mounted = false;
        };
    }, [userId]);

    return (
        <Stack gap="md">
            <RecommendationBlock items={feed?.recommended_songs} title="Recommended Songs" />
            <RecommendationBlock items={feed?.trending_in_ethiopia} title="Trending in Ethiopia" />
            <RecommendationBlock
                items={feed?.based_on_history}
                title="Based on Listening History"
            />
        </Stack>
    );
};
