import { MdMusicNote } from 'react-icons/md';

import styles from './library-list-item.module.css';

import { useItemImageUrl } from '/@/renderer/components/item-image/item-image';
import { LibraryItem } from '/@/shared/types/domain-types';

interface LibraryListItemProps {
    caption?: string;
    imageId?: null | string;
    meta: string;
    serverId?: string;
    title: string;
    type: LibraryItem;
}

export const LibraryListItem = ({
    caption,
    imageId,
    meta,
    serverId,
    title,
    type,
}: LibraryListItemProps) => {
    const imageUrl = useItemImageUrl({
        id: imageId,
        itemType: type,
        serverId,
        type: 'table',
    });

    return (
        <div className={styles.item}>
            <div className={styles.thumb}>
                {imageUrl ? <img alt={title} src={imageUrl} /> : <MdMusicNote aria-hidden />}
            </div>
            <div className={styles.copy}>
                <div className={styles.title}>{title}</div>
                <div className={styles.meta}>{meta}</div>
                {caption ? <div className={styles.caption}>{caption}</div> : null}
            </div>
        </div>
    );
};
