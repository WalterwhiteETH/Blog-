import axios from 'axios';

const backendBaseUrl =
    ((import.meta as any).env?.BACKEND_API as string | undefined) ||
    ((import.meta as any).env?.VITE_BACKEND_API as string | undefined) ||
    'http://localhost:8000';

export const backendClient = axios.create({
    baseURL: backendBaseUrl,
    timeout: 10000,
});

export type DeviceClass = 'high' | 'lite';

export interface MarketplacePlaylist {
    creator: string;
    id: string;
    number_of_followers: number;
    price: number;
    title: string;
}

export interface RecommendationPayload {
    based_on_history?: any[];
    recommended_songs?: any[];
    trending_in_ethiopia?: any[];
}

export const getUserProfile = async (userId: string) => {
    const { data } = await backendClient.get(`/users/${userId}/profile`);
    return data;
};

export const checkSubscription = async (userId: string) => {
    const { data } = await backendClient.get('/subscription/check', {
        params: { user_id: userId },
    });
    return data as { subscribed: boolean };
};

export const getMarketplacePlaylists = async () => {
    const { data } = await backendClient.get('/marketplace/playlists');
    return data as MarketplacePlaylist[];
};

export const purchasePlaylist = async (userId: string, playlistId: string) => {
    const { data } = await backendClient.post('/marketplace/buy', {
        playlist_id: playlistId,
        user_id: userId,
    });
    return data;
};

export const createPayment = async (payload: {
    amount: number;
    playlist_id?: string;
    type: 'playlist_purchase' | 'subscription_monthly' | 'wallet_topup';
    user_id: string;
}) => {
    const { data } = await backendClient.post('/payments/create', payload);
    return data as { payment_url?: string };
};

export const getRecommendations = async (userId: string) => {
    const { data } = await backendClient.get('/recommendations', {
        params: { user_id: userId },
    });
    return data as RecommendationPayload;
};

export const registerDevice = async (payload: {
    email?: string;
    telegram?: boolean;
    telegram_id?: string;
    user_agent: string;
}) => {
    const { data } = await backendClient.post('/register-device', payload);
    return data as { device_class: DeviceClass; user_id: number };
};

export const telegramLogin = async (payload: { telegram_user_id: string }) => {
    const { data } = await backendClient.post('/telegram/login', payload);
    return data;
};
