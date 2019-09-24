import { Artist } from './artist';
import { Album } from './album';
import { User } from './user';

export interface Track {
    uri: string, 
    name: string,
    artists: Artist[],
    album: Album,
    images: string[],
    requestedBy: User,
    length: Number,
    is_downvote_sound: boolean
}
 