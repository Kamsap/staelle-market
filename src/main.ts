import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app/app.component';
import { RootComponent } from './app/root.component';
import { AdminComponent } from './app/admin/admin.component';

bootstrapApplication(RootComponent, {
  providers: [
    provideHttpClient(),
    provideRouter([
      { path: 'admin', component: AdminComponent, title: 'Administration · Staelle' },
      { path: '', component: AppComponent, title: 'Staelle Market' },
      { path: '**', redirectTo: '' }
    ])
  ]
}).catch((err) => console.error(err));
