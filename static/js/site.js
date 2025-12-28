// Mobile nav toggle
(function(){
  function qs(sel, ctx){ return (ctx||document).querySelector(sel) }
  const toggle = qs('.nav-toggle');
  const nav = qs('.nav-links');
  if(!toggle || !nav) return;
  let lastFocus = null;

  function openNav(){
    lastFocus = document.activeElement;
    nav.classList.add('open');
    document.body.classList.add('nav-open');
    toggle.setAttribute('aria-expanded','true');
    toggle.classList.add('menu-open');
    nav.setAttribute('aria-hidden','false');
    // prevent background scroll
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    // focus first link
    const first = nav.querySelector('a');
    if(first) first.focus();
  }

  function closeNav(){
    nav.classList.remove('open');
    document.body.classList.remove('nav-open');
    toggle.setAttribute('aria-expanded','false');
    toggle.classList.remove('menu-open');
    nav.setAttribute('aria-hidden','true');
    // restore scroll
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    // restore focus
    if(lastFocus) lastFocus.focus();
  }

  toggle.addEventListener('click', function(e){
    const isOpen = nav.classList.contains('open');
    if(isOpen) closeNav(); else openNav();
  });

  // Close when clicking a nav link
  nav.addEventListener('click', function(e){
    const a = e.target.closest('a');
    if(a) closeNav();
  });

  // Close button inside drawer
  const navClose = document.querySelector('.nav-close');
  if(navClose){
    navClose.addEventListener('click', function(){ closeNav(); });
  }

  // Close when clicking outside (for legacy/edge cases)
  document.addEventListener('click', function(e){
    if(!nav.classList.contains('open')) return;
    if(e.target === toggle || toggle.contains(e.target)) return;
    if(nav.contains(e.target)) return;
    closeNav();
  });

  // Close on ESC
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && nav.classList.contains('open')) closeNav();
  });

})();

// Reveal-on-scroll: make sections and cards visible when they enter viewport
(function(){
  if(!('IntersectionObserver' in window)){
    // If no IO support, ensure elements are visible
    document.querySelectorAll('.section, .card').forEach(el => el.classList.add('in-view'));
    return;
  }

  document.addEventListener('DOMContentLoaded', function(){
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    document.querySelectorAll('.section, .card').forEach(el => io.observe(el));
  });
})();

// Adjust body padding to match fixed header height
(function(){
  function setBodyOffset(){
    const header = document.querySelector('header');
    if(!header) return;
    const h = header.offsetHeight || 0;
    document.body.style.paddingTop = h + 'px';
  }
  document.addEventListener('DOMContentLoaded', setBodyOffset);
  window.addEventListener('load', setBodyOffset);
  window.addEventListener('resize', setBodyOffset);
})();
