export interface PlaybackState {
    mopidy_state: string, 
    playback_enabled: boolean,
    progress_percent: number,
    progress_seconds : number,
    track_length_seconds : number
}
