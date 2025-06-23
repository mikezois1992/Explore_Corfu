const ROUTES = [
  {
    title: 'Vlaxerena',
    url: '/vlaxerena',
    position: { lat: 39.60656779533143, lng: 19.89981239373672 }
  },
  {
    title: 'Nisaki',
    url: '/Nisaki',
    position: { lat: 39.70989964469676, lng: 19.84198619413788 }
  },
  {
    title: 'Ag. Gordios',
    url: '/agGordios',
    position: { lat: 39.5442142423328, lng: 19.83537469455423 }
  },
  {
    title: 'Arkoudilas',
    url: '/arkoudilas',
    position: { lat: 39.37473498319727, lng: 20.097719694390793 }
  }
];

function initRoutesMap() {
  const map = L.map('routes-map').setView([39.62, 19.92], 11); // Κέντρο στην Κέρκυρα

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  ROUTES.forEach(route => {
  L.marker([route.position.lat, route.position.lng])
    .addTo(map)
    .bindPopup(`<a href="${route.url}">${route.title}</a>`);
  });

}

document.addEventListener('DOMContentLoaded', initRoutesMap);

