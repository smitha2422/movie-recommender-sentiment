// async function getRecommendations() {
//     const title = document.getElementById('movieInput').value;
//     const res = await fetch('/api/recommend', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ title })
//     });
//     const data = await res.json();
//     const list = document.getElementById('recommendList');
//     list.innerHTML = '';
//     if (data.error) {
//         list.innerHTML = `<li>${data.error}</li>`;
//         return;
//     }
//     data.recommendations.forEach(movie => {
//         const li = document.createElement('li');
//         li.textContent = `${movie.title} — ${movie.genres}`;
//         list.appendChild(li);
//     });
// }

// async function getSentiment() {
//     const review = document.getElementById('reviewInput').value;
//     const res = await fetch('/api/sentiment', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ review })
//     });
//     const data = await res.json();
//     const result = document.getElementById('sentimentResult');
//     result.textContent = `${data.sentiment} (${data.confidence}% confidence)`;
//     result.style.color = data.sentiment === 'Positive' ? '#4caf50' : '#f44336';
// }

async function getRecommendations() {
    const title = document.getElementById('movieInput').value;
    const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    const data = await res.json();
    const list = document.getElementById('recommendList');
    list.innerHTML = '';
    if (data.error) {
        list.innerHTML = `<li>${data.error}</li>`;
        return;
    }
    data.recommendations.forEach(movie => {
        const li = document.createElement('li');
        li.innerHTML = `${movie.title} — ${movie.genres} <button onclick="addToWatchlist('${movie.title.replace(/'/g, "\\'")}')">+ Watchlist</button>`;
        list.appendChild(li);
    });
}

async function getSentiment() {
    const review = document.getElementById('reviewInput').value;
    const res = await fetch('/api/sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review })
    });
    const data = await res.json();
    const result = document.getElementById('sentimentResult');
    result.textContent = `${data.sentiment} (${data.confidence}% confidence)`;
    result.style.color = data.sentiment === 'Positive' ? '#4caf50' : '#f44336';
    loadHistory();
}

async function addToWatchlist(title) {
    await fetch('/api/watchlist/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    loadWatchlist();
}

async function removeFromWatchlist(title) {
    await fetch('/api/watchlist/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    loadWatchlist();
}

async function loadWatchlist() {
    const res = await fetch('/api/watchlist');
    const data = await res.json();
    const list = document.getElementById('watchlistItems');
    list.innerHTML = '';
    data.watchlist.forEach(title => {
        const li = document.createElement('li');
        li.innerHTML = `${title} <button onclick="removeFromWatchlist('${title.replace(/'/g, "\\'")}')">Remove</button>`;
        list.appendChild(li);
    });
}

async function loadHistory() {
    const res = await fetch('/api/history');
    const data = await res.json();
    const list = document.getElementById('historyItems');
    list.innerHTML = '';
    data.history.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `"${item.review.slice(0, 50)}..." → ${item.sentiment} (${item.confidence}%)`;
        list.appendChild(li);
    });
}

// Load on page open
window.onload = () => {
    loadWatchlist();
    loadHistory();
};