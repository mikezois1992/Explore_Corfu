function showThankYouMessage(event) {
    event.preventDefault(); // Να μην κάνει submit/reload η φόρμα
  
    const form = document.getElementById('contact-form');
    const thankYouMessage = document.getElementById('thank-you-message');
  
    if (form && thankYouMessage) {
      // Κρύβουμε τη φόρμα με fade-out
      form.classList.add('hidden');
  
      // Περιμένουμε το fade-out να ολοκληρωθεί πριν εμφανίσουμε το μήνυμα
      setTimeout(() => {
        // Εμφανίζουμε το μήνυμα με fade-in
        thankYouMessage.classList.add('show');
      }, 500); // Περιμένουμε 0.5s για να ολοκληρωθεί το fade-out
    }
  }