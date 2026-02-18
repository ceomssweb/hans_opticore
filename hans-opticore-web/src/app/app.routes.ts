import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AboutComponent } from './components/about/about.component';
import { ServicesComponent } from './components/services/services.component';
import { ContactComponent } from './components/contact/contact.component';

export const routes: Routes = [
  { path: '', component: HomeComponent, title: 'HANS OptiCore – Optimize Operations. Reduce Costs. Accelerate Growth.' },
  { path: 'about', component: AboutComponent, title: 'About Us – HANS OptiCore' },
  { path: 'services', component: ServicesComponent, title: 'Our Services – HANS OptiCore' },
  { path: 'contact', component: ContactComponent, title: 'Contact Us – HANS OptiCore' },
  { path: '**', redirectTo: '' }
];
