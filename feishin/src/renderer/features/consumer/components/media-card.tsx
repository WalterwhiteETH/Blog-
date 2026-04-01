import clsx from 'clsx';
import { MdMusicNote } from 'react-icons/md';

import styles from './media-card.module.css';

import { useItemImageUrl } from '/@/renderer/components/item-image/item-image';
import { LibraryItem } from '/@/shared/types/domain-types';

interface MediaCardProps {
    artist: string;
    className?: string;
    imageId?: null | string;
    serverId?: string;
    subtitle?: string;
    title: string;
    type: LibraryItem;
}

export const MediaCard = ({
    artist,
    className,
    imageId,
    serverId,
    subtitle,
    title,
    type,
}: MediaCardProps) => {
    const imageUrl = useItemImageUrl({
        id: imageId,
        itemType: type,
        serverId,
        type: 'itemCard',
    });

    return (
        <div className={clsx(styles.card, className)}>
            <div className={styles.art}>
                {imageUrl ? <img alt={title} src={imageUrl} /> : <MdMusicNote aria-hidden />}
            </div>
            <div className={styles.title}>{title}</div>
            <div className={styles.meta}>{artist}</div>
            {subtitle ? <div className={styles.meta}>{subtitle}</div> : null}
        </div>
    );
};
