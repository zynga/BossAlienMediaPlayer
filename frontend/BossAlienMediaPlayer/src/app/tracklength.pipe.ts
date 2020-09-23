import { Pipe, PipeTransform } from '@angular/core';
@Pipe({
  name: 'tracklength'
})
export class TrackLengthPipe implements PipeTransform {

    transform(value: any, ...args: any[]) {
        return this.millisecondsToMS(value)
    }

    millisecondsToMS(d) : string {
        d = Number(d / 1000);
        var absd = Math.abs(d);

        var h = Math.floor(absd / 3600);
        var m = Math.floor(absd % 3600 / 60);
        var s = Math.floor(absd % 3600 % 60);

        var n = (d < 0? "-": "");

        if (h > 0) {
            return n + h + ":" + ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
        } else {
            return n + ('' + m).slice(-2) + ":" + ('0' + s).slice(-2);
        }
    }
}