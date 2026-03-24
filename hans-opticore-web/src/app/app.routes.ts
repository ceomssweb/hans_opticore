import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AboutComponent } from './components/about/about.component';
import { ServicesComponent } from './components/services/services.component';
import { ContactComponent } from './components/contact/contact.component';

export const routes: Routes = [
  { path: '', component: HomeComponent, title: 'HANS OptiCore – Operations Consulting for SMEs | Business Process Improvement India' },
  { path: 'about', component: AboutComponent, title: 'About Us – Operational Excellence Consulting India | HANS OptiCore' },
  { path: 'services', component: ServicesComponent, title: 'Our Services – Cost Reduction, Supply Chain & Inventory Optimization Consulting | HANS OptiCore' },
  { path: 'contact', component: ContactComponent, title: 'Contact Us – Start Optimizing Today for SME Business Consulting | HANS OptiCore' },
  { path: '**', redirectTo: '' }
];
