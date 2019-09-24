import { Track } from './track.interface';
import { QueuedItemMetadata } from './queued-item-metadata.interface';

export class QueuedItem {

   public track : Track;
   public metadata : QueuedItemMetadata;
}
