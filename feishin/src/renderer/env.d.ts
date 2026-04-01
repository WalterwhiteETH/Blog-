/// <reference types="vite/client" />

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

interface ImportMetaEnv {
    readonly BACKEND_API?: string;
    readonly VITE_BACKEND_API?: string;
}
