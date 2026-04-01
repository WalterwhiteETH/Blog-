import { type ComponentType, lazy, Suspense } from 'react';

import { Spinner } from '/@/shared/components/spinner/spinner';

const LazyLyricsSettingsContextModal = lazy(() =>
    import('/@/renderer/features/lyrics/components/lyrics-settings-modal').then((module) => ({
        default: module.LyricsSettingsContextModal,
    })),
);
const LazyShuffleAllContextModal = lazy(() =>
    import('/@/renderer/features/player/components/shuffle-all-modal').then((module) => ({
        default: module.ShuffleAllContextModal,
    })),
);
const LazyAddToPlaylistContextModal = lazy(() =>
    import('/@/renderer/features/playlists/components/add-to-playlist-context-modal').then(
        (module) => ({
            default: module.AddToPlaylistContextModal,
        }),
    ),
);
const LazySaveAndReplaceContextModal = lazy(() =>
    import('/@/renderer/features/playlists/components/save-and-replace-context-modal').then(
        (module) => ({
            default: module.SaveAndReplaceContextModal,
        }),
    ),
);
const LazyUpdatePlaylistContextModal = lazy(() =>
    import('/@/renderer/features/playlists/components/update-playlist-form').then((module) => ({
        default: module.UpdatePlaylistContextModal,
    })),
);
const LazySettingsContextModal = lazy(() =>
    import('/@/renderer/features/settings/components/settings-modal').then((module) => ({
        default: module.SettingsContextModal,
    })),
);
const LazyShareItemContextModal = lazy(() =>
    import('/@/renderer/features/sharing/components/share-item-context-modal').then((module) => ({
        default: module.ShareItemContextModal,
    })),
);
const LazyVisualizerSettingsContextModal = lazy(() =>
    import('/@/renderer/features/visualizer/components/audiomotionanalyzer/visualizer-settings-modal').then(
        (module) => ({
            default: module.VisualizerSettingsContextModal,
        }),
    ),
);

const withSuspense = (Component: ComponentType<any>) => (props: any) => (
    <Suspense fallback={<Spinner container />}>
        <Component {...props} />
    </Suspense>
);

export const modalRegistry = {
    addToPlaylist: withSuspense(LazyAddToPlaylistContextModal),
    lyricsSettings: withSuspense(LazyLyricsSettingsContextModal),
    saveAndReplace: withSuspense(LazySaveAndReplaceContextModal),
    settings: withSuspense(LazySettingsContextModal),
    shareItem: withSuspense(LazyShareItemContextModal),
    shuffleAll: withSuspense(LazyShuffleAllContextModal),
    updatePlaylist: withSuspense(LazyUpdatePlaylistContextModal),
    visualizerSettings: withSuspense(LazyVisualizerSettingsContextModal),
};
