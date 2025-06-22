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
  const map = new google.maps.Map(document.getElementById('routes-map'), {
    center: { lat: 39.6065, lng: 19.8998 },
    zoom: 10
  });

  ROUTES.forEach(item => {
    const marker = new google.maps.Marker({
      position: item.position,
      map,
      title: item.title
    });
    marker.addListener('click', () => {
      window.location.href = item.url;
    });
  });
}

