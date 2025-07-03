const ROUTES = [
  {
    title: 'Vlaxerena',
    url: '/vlaxerena',
    position: { lat: 39.60656779533143, lng: 19.89981239373672 },
    elevation: 2,
    terrain: 'Επίπεδο, παραθαλάσσιο',
    description: 'Μικρή νησίδα με μοναστήρι και λιμνοθάλασσα.'
  },
  {
    title: 'Nisaki',
    url: '/Nisaki',
    position: { lat: 39.70989964469676, lng: 19.84198619413788 },
    elevation: 44,
    terrain: 'Λοφώδες, ανατολική ακτή',
    description: 'Χωριό με όμορφη παραλία και θέα στην Αλβανία.'
  },
  {
    title: 'Ag. Gordios',
    url: '/agGordios',
    position: { lat: 39.5442142423328, lng: 19.83537469455423 },
    elevation: 0,
    terrain: 'Παραθαλάσσιο με λόφους',
    description: 'Δημοφιλής παραλία με χρυσή άμμο και βράχια γύρω.'
  },
  {
    title: 'Arkoudilas',
    url: '/arkoudilas',
    position: { lat: 39.37473498319727, lng: 20.097719694390793 },
    elevation: 125,
    terrain: 'Δασώδης λόφος με απότομες ακτές',
    description: 'Φυσική περιοχή με μοναστήρι και μονοπάτια.'
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


