function updateRSVP(guestId) {
    fetch(`/update_rsvp/${guestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        fetch("/get_rsp_number")
            .then(response => response.json())
            .then(updatedRspNumber => {
                // Update the displayed number of responses on the page
                const rspNumberElement = document.getElementById("rsp_number");
                if (rspNumberElement) {
                    rspNumberElement.textContent = "Number of responses: " + updatedRspNumber;
                }
            })
            .catch(error => {
                console.error('Error fetching updated number of responses:', error);
            });
        return response.json();
    })
    .then(data => {
        console.log('RSVP updated:', data);
    })
    .catch((error) => {
        console.error('Error updating RSVP:', error);
    });
}


function updateCheck(checkId) {
    fetch(`/update_check/${checkId}`, {
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
        console.log('Check aktualisiert:', data);
    })
    .catch((error) => {
        console.error('Fehler beim Aktualisieren von Check:', error);
    });
}