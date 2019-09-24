import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators, ValidatorFn, AbstractControl } from '@angular/forms';
import { AuthService } from '../auth.service';

@Component({
  selector: 'bamp-profile-editor',
  templateUrl: './profile-editor.component.html',
  styleUrls: ['./profile-editor.component.scss']
})
export class ProfileEditorComponent implements OnInit {
  profileForm :FormGroup;
  constructor(private authService: AuthService) { }

  ngOnInit() {
    this.profileForm = new FormGroup({
      alias: new FormControl(this.authService.user.alias, [
        Validators.required,
        forbiddenCharactersValidator(/[\u200B\u00A0\uFFEF\u2002\u2003\u2009\u200A\u202F󠀠]/iu) // there is an invisible space character in here from the extended unicode series: https://unicode-table.com/en/E0020/
      ])
    });
  }

  onSubmit() {
    this.authService.setAlias(this.authService.user, this.profileForm.value.alias);
    console.warn(this.profileForm.value);
  }

  get alias() {
    return this.profileForm.get('alias');
  }

}

export function forbiddenCharactersValidator(charactersRe: RegExp): ValidatorFn {
  return (control: AbstractControl): {[key: string]: any} | null => {
    const forbidden = charactersRe.test(control.value);
    return forbidden ? {'forbiddenCharacters': {value: control.value}} : null;
  };
}
