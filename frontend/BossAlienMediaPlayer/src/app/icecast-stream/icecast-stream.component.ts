import { Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { environment } from 'src/environments/environment';
import { ConfigService } from '../config.service';

const volumeKey: string = "streamVolume";

@Component({
  selector: 'bamp-icecast-stream',
  templateUrl: './icecast-stream.component.html',
  styleUrls: ['./icecast-stream.component.scss']
})

export class IcecastStreamComponent implements OnInit {

  constructor(private config: ConfigService) { }

  @ViewChild("IcecastStreamAudio") audioElement: ElementRef;

  public showStreamControls: boolean;
  public streamSource: string;
  public isStreaming: boolean;
  public isLoadingStream: boolean;
  public currentVolume: number;

  private streamSourceSubscription: Subscription;

  ngOnInit(): void {
    this.showStreamControls = environment.includeAudioStream;
    if (this.showStreamControls == false)
    {
      return;
    }

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

  connectToStream(): void {
    if (this.streamSource)
    {
      return;
    }
    var icecast_url = this.config.getValue("icecast_url");
    if (icecast_url == undefined)
    {
      return;
    }
    
    this.streamSource =  icecast_url + "/bamp?no_cache=" + Date.now();

    if (this.streamSource == undefined)
    {
      return;
    }

    console.info("Streaming audio from " + this.streamSource);

    this.audioElement.nativeElement.src = this.streamSource;
    this.isLoadingStream = true;

    this.audioElement.nativeElement.addEventListener("loadedmetadata", (event) => {
      this.isLoadingStream = false;
      this.isStreaming = true;
      this.audioElement.nativeElement.volume = this.currentVolume;
      this.audioElement.nativeElement.play();
    });
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
