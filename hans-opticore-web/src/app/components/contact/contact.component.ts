import { Component, OnInit, AfterViewInit, PLATFORM_ID, Inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { isPlatformBrowser, ViewportScroller } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent implements OnInit, AfterViewInit {
  private isBrowser: boolean;

  formData = {
    name: '',
    email: '',
    phone: '',
    company: '',
    service: '',
    message: ''
  };

  formSubmitted = false;

  constructor(
    @Inject(PLATFORM_ID) platformId: Object,
    private viewportScroller: ViewportScroller
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit() {
    if (this.isBrowser) {
      this.viewportScroller.scrollToPosition([0, 0]);
    }
  }

  ngAfterViewInit() {
    if (this.isBrowser) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

      document.querySelectorAll('.animate-fade-up, .animate-fade-in, .animate-scale-in').forEach(el => {
        observer.observe(el);
      });
    }
  }

  onSubmit() {
    const subject = encodeURIComponent(`Consultation Request from ${this.formData.name}`);
    const body = encodeURIComponent(
      `Name: ${this.formData.name}\n` +
      `Email: ${this.formData.email}\n` +
      `Phone: ${this.formData.phone}\n` +
      `Company: ${this.formData.company}\n` +
      `Service Interest: ${this.formData.service}\n` +
      `Message: ${this.formData.message}`
    );
    window.open(`mailto:info@hansopticore.com?subject=${subject}&body=${body}`, '_self');
    this.formSubmitted = true;
  }
}
