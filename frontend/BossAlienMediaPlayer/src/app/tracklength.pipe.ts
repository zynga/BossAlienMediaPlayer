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

        var h = Math.floor(d / 3600);
        var m = Math.floor(d % 3600 / 60);
        var s = Math.floor(d % 3600 % 60);

        if (h > 0) {
            return h + ":" + ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
        } else {
            return ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
        }
    }
}