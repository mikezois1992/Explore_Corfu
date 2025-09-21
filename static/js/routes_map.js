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
  },
  {
    title: 'Loggs',
    url: '/loggas',
    position: { lat: 39.788372986651034, lng: 19.66685356579295 }, 
    elevation: 'το επίπεδο της παραλίας είναι πρακτικά στο μηδέν, δηλαδή στο επίπεδο της θάλασσας. Οι βραχώδεις κορυφές πάνω από αυτήν αγγίζουν μέχρι 105 m.',
    terrain: 'όχι εύκολη διαδομή',
    description: 'στενή λωρίδα αμμώδους/αργιλώδους παραλίας',
    image: '/static/img/loggas peroulades-20250717T175654Z-1-001/loggas peroulades/1.jpg'
  },
  {
    title: 'Canal',
    url: '/canal',
    position: { lat: 39.797028111633345, lng: 19.69802862278645 },  
    elevation: 'μεταξύ 13–29 ft, δηλαδή περίπου 4–9 μέτρα πάνω από το επίπεδο της θάλασσας, ανάλογα με το σημείο',
    terrain: 'Βραχώδες / Κανάλια, μικρή άμμος',
    description: 'Βραχώδες / Κανάλια, μικρή άμμος',
    image: '/static/img/canal/canal damour/1.jpg'
  },
  {
    title: 'Ermones',
    url: '/ermones',
    position: { lat: 39.610643947573266, lng: 19.77796491380511 },  
    elevation: 'Η τοποθεσία Έρμονες βρίσκεται κυριολεκτικά πάνω στη θάλασσα, με ελάχιστο υψόμετρο',
    terrain: 'εύκολη διαδομή – κατάλληλη για όλους.',
    description: 'Η παραλία είναι μεικτή με βότσαλα και πετρώδη στοιχεία, καθώς πρόκειται για έναν κόλπο που περιβάλλεται από γκρεμούς και πράσινους λόφους, δημιουργώντας μια ατμόσφαιρα με έντονα φυσικά χαρακτηριστικά',
    image: '/static/img/ermones/ermones ekklisaki/1.jpg'
  },
  {
    title: 'Giannades',
    url: '/giannades',
    position: { lat: 39.630422238067766, lng: 19.76331610069776 },
    elevation: '~150 μ',
    terrain: 'εύκολη διαδομή – κατάλληλη για όλους.',
    description: 'Αυθεντικό βουνίσιο τοπίο: ηρεμία, φύση, αυθεντική αγροτική ζωή',
    image: '/static/img/giannades/Προφήτης Ηλίας- Γιαννάδες/1.jpg'
  },
  {
    title: 'Makrades',
    url: '/makrades',
    position: { lat: 39.688473001900796, lng: 19.68884659534223 }, 
    elevation: '295–318 m',
    terrain: 'εύκολη διαδομή – κατάλληλη για όλους.',
    description: ' Ιδανικό σημείο εκκίνησης για πεζοπορίες και εξερεύνηση του βορειοδυτικού άκρου του νησιού ',
    image: '/static/img/makrades/makrades/1.jpg'
  },
  {
    title: 'Cape_Drastis',
    url: '/Cape_Drastis',
    position: { lat: 39.79872004396612, lng: 19.67381089553243 },
    elevation: 'περίπου 3 μέτρα πάνω από τη θάλασσα στα χαμηλότερα σημεία',
    terrain: 'Το μονοπάτι θεωρείται μέτριας δυσκολίας λόγω του ανάγλυφου — κυμαίνεται μεταξύ -1 μ. (παραλία) και ~102 μ. κορυφή', 
    description: 'Στο βορειοδυτικό άκρο της Κέρκυρας, κοντά στο χωριό Περουλάδες, εντυπωσιακοί λευκοί βράχοι που πέφτουν κάθετα στη θάλασσα και γαλαζοπράσινα νερά.',
    image: '/static/img/cape drastis/1.jpg'
  },
  {
    title: 'MonRepos',
    url: '/MonReos',
    position: { lat:  39.61013563708864, lng: 19.92732330901196 },
    elevation: '35–40 μέτρα πάνω από τη θάλασσα.',
    terrain: 'Ελαφρώς επικλινές και λοφώδες έδαφος με χαμηλούς λόφους, πεζοπορικά μονοπάτια και δασική βλάστηση. ', 
    description: 'Δεν είναι δύσκολη η πρόσβαση, κατάλληλο για περπάτημα.',
    image: '/static/img/mon repo/1.jpg'
  },
  {
    title: 'nimfes',
    url: '/nimfes',
    position: { lat:  39.75091482023042, lng: 19.805129637856776 },
    elevation: 'περίπου 148 μ',
    terrain: 'Χωματόδρομος με ίσως ανηφορικά/κατηφορικά σημεία ', 
    description: 'εύκολη προς μέτρια διαδρομή',
    image: '/static/img/Καταρράκτες Νυμφές/1.jpg'
  },
  {
    title: 'Old Fortress',
    url: '/oldFort',
    position: { lat:  39.624064992943545, lng: 19.92785386853177},  
    elevation: '~60 μέτρα πάνω από την επιφάνεια της θάλασσας',
    terrain: 'βραχώδες ασβεστολιθικό, με απότομα σημεία, πετρόχτιστες σκάλες και μονοπάτια που οδηγούν ως την κορυφή ', 
    description: 'υπάρχουν ανηφοριές και σκαλιά',
    image: '/static/img/palaio frourio/6.jpg'
  },
  {
    title: 'Porto Timoni',
    url: '/porto_timoni',
    position: { lat:  39.71551228857589, lng: 19.65793458157802 },  
    elevation: 'περίπου 130 μέτρα.',
    terrain: 'βραχώδες και ανηφορικό/κατηφορικό, με μονοπάτι πεζοπορικό που κατεβαίνει μέσα από θάμνους, χωμάτινα σημεία και πετρώδη περάσματα', 
    description: 'Η παραλία είναι προσβάσιμη μόνο με πεζοπορία ή βάρκα',
    image: '/static/img/Πόρτο Τιμόνι-αφιωνας/16.jpg'
  },
  {
    title: 'Perama',
    url: '/perama',
    position: { lat:  39.58287914400098, lng: 19.913985372773638 },  
    elevation: '~0–20 μέτρα υψόμετρο.',
    terrain: 'ελαφρά ανηφορικά και κατηφορικά τμήματα, κυρίως χωμάτινα μονοπάτια', 
    description: 'Ο δρόμος του νερού',
    image: '/static/img/dromos toy nerou perama/2.jpg'
  },
  {
    title: 'Gastouri',
    url: '/Gastouri',
    position: { lat:  39.56081200833922, lng: 19.901700340886574 },  
    elevation: '~0–20 μέτρα υψόμετρο.',
    terrain: 'ελαφρά ανηφορικά και κατηφορικά τμήματα, κυρίως χωμάτινα μονοπάτια', 
    description: 'Περιβάλλεται από ελαιώνες',
    image: '/static/img/dromos toy nerou perama/2.jpg'
  },
  {
    title: 'Stavros',
    url: '/stavros',
    position: { lat:  39.53192490198832, lng: 19.906588303186936},  
    elevation: '~300 μ. υψόμετρο.',
    terrain: 'οργανωμένα χωμάτινα μονοπάτια, ανηφορική πλαγιά', 
    description: 'Ο δρόμος του νερού',
    image: '/static/img/stavros loop/1.jpg'
    
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


