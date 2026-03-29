import { Component, OnInit, AfterViewInit, PLATFORM_ID, Inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { isPlatformBrowser, ViewportScroller } from '@angular/common';

@Component({
  selector: 'app-services',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './services.component.html',
  styleUrl: './services.component.scss'
})
export class ServicesComponent implements OnInit, AfterViewInit {
  private isBrowser: boolean;

  constructor(
    @Inject(PLATFORM_ID) platformId: Object,
    private viewportScroller: ViewportScroller,
    private route: ActivatedRoute
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
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
}
