import { Component, OnInit, AfterViewInit, PLATFORM_ID, Inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { isPlatformBrowser, ViewportScroller, NgClass } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, NgClass],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent implements OnInit, AfterViewInit {
  private isBrowser: boolean;

  contactForm!: FormGroup;
  isSending = signal(false);
  alertState = signal<{ show: boolean; type: 'success' | 'error'; title: string; message: string }>({
    show: false, type: 'success', title: '', message: ''
  });

  constructor(
    @Inject(PLATFORM_ID) platformId: Object,
    private viewportScroller: ViewportScroller,
    private route: ActivatedRoute,
    private fb: FormBuilder
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    this.initForm();
  }

  private initForm() {
    this.contactForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.pattern(/^\+?[\d\s\-()]{7,15}$/)]],
      company: [''],
      service: [''],
      message: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  ngOnInit() {
    if (this.isBrowser) {
      this.route.fragment.subscribe(fragment => {
        if (fragment) {
          setTimeout(() => {
            const el = document.getElementById(fragment);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }, 300);
        } else {
          this.viewportScroller.scrollToPosition([0, 0]);
        }
      });
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
    if (this.contactForm.invalid) {
      this.contactForm.markAllAsTouched();
      return;
    }

    const v = this.contactForm.value;
    const to = 'info@hansopticore.com';
    const subject = encodeURIComponent(`Consultation Request from ${v.name}`);
    const body = encodeURIComponent(
      `Name: ${v.name}\n` +
      `Email: ${v.email}\n` +
      `Phone: ${v.phone || 'Not provided'}\n` +
      `Company: ${v.company || 'Not provided'}\n` +
      `Service Interest: ${v.service || 'Not specified'}\n\n` +
      `Message:\n${v.message}`
    );

    const mailtoLink = `mailto:${to}?subject=${subject}&body=${body}`;
    window.location.href = mailtoLink;

    this.showAlert('success', 'Email Client Opened!', 'Your email client has been opened with the message pre-filled. Please click Send in your email app to deliver it.');
    this.contactForm.reset();
  }

  showAlert(type: 'success' | 'error', title: string, message: string) {
    this.alertState.set({ show: true, type, title, message });
    if (type === 'success') {
      setTimeout(() => this.dismissAlert(), 8000);
    }
  }

  dismissAlert() {
    this.alertState.update(s => ({ ...s, show: false }));
  }

  get f() {
    return this.contactForm.controls;
  }
}
