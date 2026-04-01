import { useEffect, useState } from 'react';

import {
    getMarketplacePlaylists,
    MarketplacePlaylist,
    purchasePlaylist,
} from '/@/renderer/api/client';
import { useCurrentServer } from '/@/renderer/store';
import { Button } from '/@/shared/components/button/button';
import { Group } from '/@/shared/components/group/group';
import { Stack } from '/@/shared/components/stack/stack';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';

const MarketplacePage = () => {
    const currentServer = useCurrentServer();
    const userId = currentServer?.userId || '1';
    const [items, setItems] = useState<MarketplacePlaylist[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        let mounted = true;
        const load = async () => {
            setLoading(true);
            try {
                const data = await getMarketplacePlaylists();
                if (mounted) setItems(data);
            } catch (error: any) {
                toast.error({ message: error?.message || 'network error', title: 'Marketplace' });
            } finally {
                if (mounted) setLoading(false);
            }
        };
        load();
        return () => {
            mounted = false;
        };
    }, []);

    const handleBuy = async (playlistId: string) => {
        try {
            await purchasePlaylist(userId, playlistId);
            toast.success({ message: 'Playlist purchased successfully', title: 'Marketplace' });
        } catch (error: any) {
            toast.error({ message: error?.message || 'payment failed', title: 'Marketplace' });
        }
    };

    return (
        <Stack gap="md" p="lg">
            <Text fw={700} size="xl">
                Playlist Marketplace
            </Text>
            {loading && <Text variant="secondary">Loading marketplace...</Text>}
            {!loading &&
                items.map((playlist) => (
                    <Stack
                        className="telegram-panel"
                        gap="xs"
                        key={playlist.id}
                        p="md"
                        style={{
                            background: 'var(--theme-colors-surface)',
                            borderRadius: 12,
                        }}
                    >
                        <Text fw={600}>{playlist.title}</Text>
                        <Text variant="secondary">Creator: {playlist.creator}</Text>
                        <Text variant="secondary">Price: ETB {playlist.price}</Text>
                        <Text variant="secondary">Followers: {playlist.number_of_followers}</Text>
                        <Group>
                            <Button variant="default">Preview</Button>
                            <Button
                                className="telegram-primary-btn"
                                onClick={() => handleBuy(playlist.id)}
                            >
                                Buy Playlist
                            </Button>
                        </Group>
                    </Stack>
                ))}
        </Stack>
    );
};

export default MarketplacePage;
