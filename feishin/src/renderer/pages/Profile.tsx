import { useEffect, useState } from 'react';

import { getUserProfile } from '/@/renderer/api/client';
import { useCurrentServer } from '/@/renderer/store';
import { Stack } from '/@/shared/components/stack/stack';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';

const ProfilePage = () => {
    const currentServer = useCurrentServer();
    const userId = currentServer?.userId || '1';
    const [profile, setProfile] = useState<any>(null);

    useEffect(() => {
        let mounted = true;
        const load = async () => {
            try {
                const data = await getUserProfile(userId);
                if (mounted) setProfile(data);
            } catch (error: any) {
                toast.error({ message: error?.message || 'network error', title: 'Profile' });
            }
        };
        load();
        return () => {
            mounted = false;
        };
    }, [userId]);

    return (
        <Stack gap="md" p="lg">
            <Text fw={700} size="xl">
                Profile
            </Text>
            <Text variant="secondary">User ID: {userId}</Text>
            {profile ? (
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(profile, null, 2)}
                </pre>
            ) : (
                <Text variant="secondary">Loading profile...</Text>
            )}
        </Stack>
    );
};

export default ProfilePage;
