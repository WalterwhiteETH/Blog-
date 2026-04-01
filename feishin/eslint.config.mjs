import eslintConfigPrettier from '@electron-toolkit/eslint-config-prettier';
import tseslint from '@electron-toolkit/eslint-config-ts';
import perfectionist from 'eslint-plugin-perfectionist';
import eslintPluginReact from 'eslint-plugin-react';
import eslintPluginReactHooks from 'eslint-plugin-react-hooks';
import eslintPluginReactRefresh from 'eslint-plugin-react-refresh';

export default tseslint.config(
    {
        ignores: ['**/coverage', '**/dist', '**/node_modules', '**/out'],
    },
    tseslint.configs.recommended,
    perfectionist.configs['recommended-natural'],
    eslintPluginReact.configs.flat.recommended,
    eslintPluginReact.configs.flat['jsx-runtime'],
    {
        settings: {
            react: {
                version: 'detect',
            },
        },
    },
    {
        files: ['**/*.{ts,tsx}'],
        plugins: {
            'react-hooks': eslintPluginReactHooks,
            'react-refresh': eslintPluginReactRefresh,
        },
        rules: {
            ...eslintPluginReactHooks.configs.recommended.rules,
            ...eslintPluginReactRefresh.configs.vite.rules,
            '@typescript-eslint/explicit-function-return-type': 'off',
            '@typescript-eslint/no-duplicate-enum-values': 'off',
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/no-unused-vars': 'warn',
            curly: ['error', 'all'],
            'no-unused-vars': 'off',
            'no-use-before-define': 'off',
            'perfectionist/sort-exports': [
                'error',
                {
                    order: 'asc',
                    type: 'natural',
                },
            ],
            'perfectionist/sort-named-exports': [
                'error',
                {
                    order: 'asc',
                    type: 'natural',
                },
            ],
            quotes: ['error', 'single'],
            'react-hooks/refs': 'off',
            'react-hooks/set-state-in-effect': 'off',
            'react-refresh/only-export-components': 'off',
            'react/display-name': 'off',
            semi: ['error', 'always'],
            'single-attribute-per-line': 'off',
        },
    },
    eslintConfigPrettier,
);
