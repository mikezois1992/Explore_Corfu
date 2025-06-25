function initLiveSearch() {
    const input = document.getElementById('search-input');
    const suggestions = document.getElementById('suggestions');

    input.addEventListener('input', () => {
        const query = input.value.trim();
        if (query.length === 0) {
            suggestions.innerHTML = '';
            return;
        }

        fetch(`/suggest?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Data που γύρισε:", data);
                suggestions.innerHTML = '';

                data.forEach(item => {
                    const li = document.createElement('li');
                    li.classList.add('suggestion-item');

                    const a = document.createElement('a');
                    a.href = "#"; // placeholder, redirect γίνεται με JS
                    a.classList.add('suggestion-link');

                    a.innerHTML = `
                        <img src="${item.image}" alt="${item.title}" />
                        <div class="suggestion-info">
                            <strong>${item.title}</strong>
                            <p>${item.description}</p>
                        </div>
                    `;

                    a.addEventListener('click', (event) => {
                        event.preventDefault(); // μπλοκάρουμε default <a> href
                        input.value = item.title;
                        suggestions.innerHTML = '';
                         fetch('/search', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ location: item.title })
                        })
                        .catch(err => {
                            console.error('Error logging search:', err);
                        })
                        .finally(() => {
                            console.log("👉 Redirecting to:", item.url);
                            window.location.href = item.url; // 🔥 redirect χειροκίνητα
                        });

                    li.appendChild(a);
                    suggestions.appendChild(li);
                });
            })
            .catch(error => {
                console.error("Σφάλμα στο fetch:", error);
            });
    });

    // Καθάρισμα suggestions όταν γίνεται click εκτός
    document.addEventListener('click', function (e) {
        if (!document.querySelector('.search-wrapper').contains(e.target)) {
            suggestions.innerHTML = '';
        }
    });
}
