import { Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import { environment } from 'src/environments/environment';

const volumeKey: string = "streamVolume";

@Component({
  selector: 'bamp-icecast-stream',
  templateUrl: './icecast-stream.component.html',
  styleUrls: ['./icecast-stream.component.scss']
})

export class IcecastStreamComponent implements OnInit {

  constructor() { }

  @ViewChild("IcecastStreamAudio") audioElement: ElementRef;

  public streamSource: string;
  public isStreaming: boolean;
  public currentVolume: number;

  ngOnInit(): void {
    this.isStreaming = environment.includeAudioStream;
    if (this.isStreaming == false)
    {
      return;
    }
    this.streamSource = "http://" + window.location.hostname + ":8000/bamp"

    console.info("Streaming audio from " + this.streamSource);

    var savedVolumeString = localStorage.getItem(volumeKey);
    if (savedVolumeString)
    {
      this.currentVolume = parseFloat(savedVolumeString);
    }
    else
    {
      this.currentVolume = 1.0;
      localStorage.setItem(volumeKey, "" + this.currentVolume);
    }
  }

  onVolumeChanged(): void {
    this.audioElement.nativeElement.volume = this.currentVolume;
    localStorage.setItem(volumeKey, "" + this.currentVolume);
  }

  onMute(): void {
    this.currentVolume = 0;
    this.onVolumeChanged();
  }

  onMaxVolume(): void {
    this.currentVolume = 1;
    this.onVolumeChanged();
  }
}
