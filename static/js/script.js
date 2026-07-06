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
        li.textContent = `${movie.title} — ${movie.genres}`;
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
}