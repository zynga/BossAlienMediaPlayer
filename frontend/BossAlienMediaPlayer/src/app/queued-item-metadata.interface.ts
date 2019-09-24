export interface QueuedItemMetadata {
    upvotes: number, 
    downvotes: number,
    track_uri: string,
    user_id: string,
    actions: string[],
    reasons: string[],
    userUpvotedTrack: boolean,
    userDownvotedTrack: boolean
}
