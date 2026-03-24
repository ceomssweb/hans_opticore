import { Component, OnInit, AfterViewInit, PLATFORM_ID, Inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { isPlatformBrowser, ViewportScroller, NgClass } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import emailjs from '@emailjs/browser';

// ── EmailJS Configuration ──
// Replace these with your actual EmailJS credentials from https://www.emailjs.com/
const EMAILJS_PUBLIC_KEY = '8PIFiZD3z_n9RTiNz';
const EMAILJS_SERVICE_ID = 'service_eld67ds';
const EMAILJS_TEMPLATE_ID = 'YOUR_TEMPLATE_ID';

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
      emailjs.init(EMAILJS_PUBLIC_KEY);
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

  async onSubmit() {
    if (this.contactForm.invalid) {
      this.contactForm.markAllAsTouched();
      return;
    }

    this.isSending.set(true);
    const formValue = this.contactForm.value;

    const templateParams = {
      from_name: formValue.name,
      from_email: formValue.email,
      phone: formValue.phone || 'Not provided',
      company: formValue.company || 'Not provided',
      service: formValue.service || 'Not specified',
      message: formValue.message,
      reply_to: formValue.email
    };

    try {
      await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, templateParams);
      this.showAlert('success', 'Message Sent!', 'Your consultation request has been delivered successfully. We\'ll get back to you within 24 hours.');
      this.contactForm.reset();
    } catch {
      this.showAlert('error', 'Oops! Something went wrong', 'We couldn\'t send your message right now. Please try again or reach out directly at info@hansopticore.com');
    } finally {
      this.isSending.set(false);
    }
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
