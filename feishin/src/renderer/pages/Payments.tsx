import { createPayment } from '/@/renderer/api/client';
import { useCurrentServer } from '/@/renderer/store';
import { Button } from '/@/shared/components/button/button';
import { Stack } from '/@/shared/components/stack/stack';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';

const PaymentsPage = () => {
    const currentServer = useCurrentServer();
    const userId = currentServer?.userId || '1';

    const handlePayment = async (
        type: 'playlist_purchase' | 'subscription_monthly' | 'wallet_topup',
    ) => {
        try {
            const amount = type === 'subscription_monthly' ? 199 : 50;
            const result = await createPayment({
                amount,
                type,
                user_id: userId,
            });

            if (!result.payment_url) {
                toast.error({ message: 'payment failed', title: 'Payments' });
                return;
            }

            window.location.href = result.payment_url;
        } catch (error: any) {
            toast.error({ message: error?.message || 'payment failed', title: 'Payments' });
        }
    };

    return (
        <Stack gap="md" p="lg">
            <Text fw={700} size="xl">
                Payments
            </Text>
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Subscription</Text>
                <Text size="sm" variant="secondary">
                    Unlimited premium tracks for one month.
                </Text>
                <Button
                    className="telegram-primary-btn"
                    onClick={() => handlePayment('subscription_monthly')}
                >
                    Subscribe monthly
                </Button>
            </Stack>
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Wallet</Text>
                <Text size="sm" variant="secondary">
                    Add balance to buy playlists and premium content.
                </Text>
                <Button onClick={() => handlePayment('wallet_topup')}>Top-up wallet</Button>
            </Stack>
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Playlist Purchase</Text>
                <Text size="sm" variant="secondary">
                    Buy curated Ethiopian playlists from creators.
                </Text>
                <Button onClick={() => handlePayment('playlist_purchase')}>
                    Purchase playlist
                </Button>
            </Stack>
        </Stack>
    );
};

export default PaymentsPage;
