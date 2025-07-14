const ROUTES = [
  {
    title: 'Vlaxerena',
    url: '/vlaxerena',
    position: { lat: 39.60656779533143, lng: 19.89981239373672 },
    elevation: 2,
    terrain: 'Επίπεδο, παραθαλάσσιο',
    description: 'Μικρή νησίδα με μοναστήρι και λιμνοθάλασσα.',
    image: '/static/img/Vlaxerena/vlaxerna/icon1.jpg'
  },
  {
    title: 'Nisaki',
    url: '/Nisaki',
    position: { lat: 39.70989964469676, lng: 19.84198619413788 },
    elevation: 44,
    terrain: 'Λοφώδες, ανατολική ακτή',
    description: 'Χωριό με όμορφη παραλία και θέα στην Αλβανία.',
    image: '/static/img/Nisaki/nisaki pezoporia/icon1.jpg'
  },
  {
    title: 'Ag. Gordios',
    url: '/agGordios',
    position: { lat: 39.5442142423328, lng: 19.83537469455423 },
    elevation: 0,
    terrain: 'Παραθαλάσσιο με λόφους',
    description: 'Δημοφιλής παραλία με χρυσή άμμο και βράχια γύρω.',
    image: '/static/img/Ag.Gorgios/nayagio agios gordis-20250524T162344Z-1-001/nayagio agios gordis/icon1.jpg'
  },
  {
    title: 'Arkoudilas',
    url: '/arkoudilas',
    position: { lat: 39.37473498319727, lng: 20.097719694390793 },
    elevation: 125,
    terrain: 'Δασώδης λόφος με απότομες ακτές',
    description: 'Φυσική περιοχή με μοναστήρι και μονοπάτια.',
    image: '/static/img/arkoudilas/arkoudilas/icon1.jpg'
  },
  {
    title: 'Erimitis',
    url: '/erimitis',
    position: { lat: 39.776846245788605, lng: 19.948111715082188 }, 
    elevation: 'Ανέβασμα/κατέβασμα ~55 m, με ελάχιστο υψόμετρο ~ −1 m και μέγιστο ~ 52 m',
    terrain: 'εύκολη διαδομή – κατάλληλη για όλους.',
    description: 'πυκνή μεσογειακή βλάστηση, απόκρημνες ακτές, μικρούς όρμους, τρεις λίμνες',
    image: '/static/img/Erimitis/erimitis/Ερημίτης/1.jpg'
  }
];

function initRoutesMap() {
  const map = L.map('routes-map').setView([39.62, 19.92], 11); // Κέντρο στην Κέρκυρα

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  const bounds = L.latLngBounds([]);

  ROUTES.forEach(route => {
      const popupContent = `
      <a href="${route.url}">${route.title}</a><br/>
      <img src="${route.image}" alt="${route.title}" style="width:100px;height:auto;"/><br/>
      <strong>Υψόμετρο:</strong> ${route.elevation} μ.<br/>
      <strong>Έδαφος:</strong> ${route.terrain}<br/>
      ${route.description}
    `;
    const marker = L.marker([route.position.lat, route.position.lng])
      .addTo(map)
      .bindPopup(popupContent);
    
    bounds.extend(marker.getLatLng());
  });

  map.fitBounds(bounds);
}
 

document.addEventListener('DOMContentLoaded', initRoutesMap);


