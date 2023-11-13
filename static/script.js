function updateRSVP(guestId) {
    fetch(`/update_rsvp/${guestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('RSVP aktualisiert:', data);
    })
    .catch((error) => {
        console.error('Fehler beim Aktualisieren von RSVP:', error);
    });
}