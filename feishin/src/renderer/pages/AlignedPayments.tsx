import { useState, useEffect } from 'react';
import {
    createPayment,
    confirmPayment,
    checkSubscription,
    getPaymentProviders,
    handleApiError,
    type LegacyPayment,
    getBackendUserId,
} from '/@/renderer/api/aligned-client';
import { Button } from '/@/shared/components/button/button';
import { Stack } from '/@/shared/components/stack/stack';
import { Text } from '/@/shared/components/text/text';
import { toast } from '/@/shared/components/toast/toast';

const AlignedPaymentsPage = () => {
    const userId = getBackendUserId();
    const [loading, setLoading] = useState(false);
    const [subscriptionStatus, setSubscriptionStatus] = useState<{ subscribed: boolean } | null>(null);
    const [currentPayment, setCurrentPayment] = useState<LegacyPayment | null>(null);
    const [selectedProvider, setSelectedProvider] = useState('telebirr');

    const paymentProviders = getPaymentProviders();

    useEffect(() => {
        loadSubscriptionStatus();
    }, [userId]);

    const loadSubscriptionStatus = async () => {
        try {
            const status = await checkSubscription(userId);
            setSubscriptionStatus(status);
        } catch (error) {
            console.error('Failed to load subscription status:', error);
        }
    };

    const handlePayment = async (
        type: 'playlist_purchase' | 'song_purchase' | 'subscription_monthly' | 'wallet_topup',
    ) => {
        setLoading(true);
        try {
            const amount = type === 'subscription_monthly' ? 199 : type === 'song_purchase' ? 25 : 50;
            
            // Step 1: Create payment
            const payment = await createPayment({
                amount,
                method: selectedProvider as 'telebirr' | 'cbe',
                user_id: userId,
                payment_type: type,
            });

            setCurrentPayment(payment);
            
            toast.success({
                message: `Payment ${payment.id} created with status ${payment.status}.`,
                title: 'Payment Created',
            });

            // Step 2: For demo purposes, auto-confirm after 2 seconds
            // In real implementation, this would happen after actual payment
            setTimeout(async () => {
                try {
                    const result = await confirmPayment({
                        payment_id: payment.id,
                    });

                    toast.success({
                        message: `Payment confirmed! Status: ${result.status}`,
                        title: 'Payment Complete',
                    });

                    // Reload subscription status
                    await loadSubscriptionStatus();
                    setCurrentPayment(null);
                } catch (error) {
                    toast.error({
                        message: 'Payment confirmation failed',
                        title: 'Confirmation Error',
                    });
                }
            }, 2000);

        } catch (error: any) {
            const apiError = handleApiError(error);
            toast.error({ 
                message: apiError.message, 
                title: 'Payment Failed' 
            });
        } finally {
            setLoading(false);
        }
    };

    const formatPrice = (amount: number) => {
        return new Intl.NumberFormat('et-ET', {
            style: 'currency',
            currency: 'ETB',
        }).format(amount);
    };

    return (
        <Stack gap="lg" p="lg">
            <Text fw={700} size="xl">
                Payments
            </Text>

            {/* Current Subscription Status */}
            {subscriptionStatus && (
                <Stack className="telegram-panel" gap="md" p="md">
                    <Text fw={600}>Subscription Status</Text>
                    {subscriptionStatus.subscribed ? (
                        <Stack gap="sm">
                            <Text size="sm" className="text-green-500">
                                ✅ Active Subscription
                            </Text>
                            <Text size="sm" variant="secondary">
                                You have access to premium features
                            </Text>
                        </Stack>
                    ) : (
                        <Stack gap="sm">
                            <Text size="sm" variant="secondary">
                                No active subscription
                            </Text>
                            <Text size="sm" variant="secondary">
                                Subscribe to unlock premium features
                            </Text>
                        </Stack>
                    )}
                </Stack>
            )}

            {/* Payment Provider Selection */}
            <Stack className="telegram-panel" gap="md" p="md">
                <Text fw={600}>Payment Method</Text>
                <Stack gap="sm">
                    {paymentProviders.map((provider) => (
                        <Button
                            key={provider.id}
                            className={`telegram-secondary-btn ${selectedProvider === provider.id ? 'selected' : ''}`}
                            onClick={() => setSelectedProvider(provider.id)}
                            variant={selectedProvider === provider.id ? 'primary' : 'secondary'}
                        >
                            <Stack direction="row" gap="sm" align="center">
                                <Text>{provider.name}</Text>
                                <Text size="xs" variant="secondary">
                                    ({provider.description})
                                </Text>
                            </Stack>
                        </Button>
                    ))}
                </Stack>
            </Stack>

            {/* Subscription Options */}
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Subscription</Text>
                <Text size="sm" variant="secondary">
                    Unlimited premium tracks for one month.
                </Text>
                <Button
                    className="telegram-primary-btn"
                    onClick={() => handlePayment('subscription_monthly')}
                    disabled={loading || subscriptionStatus?.subscribed}
                >
                    {loading ? 'Processing...' : 'Subscribe monthly - 199 ETB'}
                </Button>
            </Stack>

            {/* Wallet Top-up */}
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Wallet</Text>
                <Text size="sm" variant="secondary">
                    Add funds to your wallet for purchases.
                </Text>
                <Button
                    className="telegram-secondary-btn"
                    onClick={() => handlePayment('wallet_topup')}
                    disabled={loading}
                >
                    {loading ? 'Processing...' : 'Top-up wallet - 50 ETB'}
                </Button>
            </Stack>

            {/* Song Purchase */}
            <Stack className="telegram-panel" gap="sm" p="md">
                <Text fw={600}>Purchase Song</Text>
                <Text size="sm" variant="secondary">
                    Buy individual songs for permanent access.
                </Text>
                <Button
                    className="telegram-secondary-btn"
                    onClick={() => handlePayment('song_purchase')}
                    disabled={loading}
                >
                    {loading ? 'Processing...' : 'Buy song - 25 ETB'}
                </Button>
            </Stack>

            {/* Payment Processing Status */}
            {currentPayment && (
                <Stack className="telegram-panel" gap="md" p="md">
                    <Text fw={600}>Payment Processing</Text>
                    <Text size="sm" variant="secondary">
                        Payment ID: {currentPayment.id}
                    </Text>
                    <Text size="sm" variant="secondary">
                        Amount: {formatPrice(currentPayment.amount)}
                    </Text>
                    <Text size="sm" variant="secondary">
                        Method: {currentPayment.method}
                    </Text>
                    <Text size="sm" variant="secondary">
                        Status: {currentPayment.status}
                    </Text>
                    <Text size="sm" className="text-blue-500">
                        Processing payment with {selectedProvider}...
                    </Text>
                    <Text size="xs" variant="secondary">
                        This is a demo - payment will be confirmed automatically
                    </Text>
                </Stack>
            )}

            {/* Features */}
            <Stack className="telegram-panel" gap="md" p="md">
                <Text fw={600}>Premium Features</Text>
                <Stack gap="sm">
                    <Text size="sm">✓ Unlimited premium tracks</Text>
                    <Text size="sm">✓ High-quality audio</Text>
                    <Text size="sm">✓ Offline downloads</Text>
                    <Text size="sm">✓ No advertisements</Text>
                    <Text size="sm">✓ Advanced search</Text>
                </Stack>
            </Stack>
        </Stack>
    );
};

export default AlignedPaymentsPage;
