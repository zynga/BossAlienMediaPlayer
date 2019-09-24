import { Track } from './track.interface';

export class HistoryItem {
    upvotes: number;
    downvotes: number;
    epoch: number;
    track: Track;
    was_voted_off: boolean;
}
