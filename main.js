// Fetch videos from Flask backend
async function fetchVideos(query) {
  const resp = await fetch('/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query, maxResults: 8 })
  });
  return resp.json();
}

// Escape HTML to prevent XSS
function escapeHtml(str){
  if(!str) return '';
  return str.replaceAll('&','&amp;')
            .replaceAll('<','&lt;')
            .replaceAll('>','&gt;');
}

// Build a Bootstrap carousel dynamically
function buildCarousel(videos) {
  if (!videos || videos.length === 0) return '<p>No videos found.</p>';

  const id = 'ytCarousel';
  let indicators = '<div class="carousel-indicators">';
  let inner = '<div class="carousel-inner">';

  videos.forEach((v, i) => {
    indicators += `<button type="button" data-bs-target="#${id}" data-bs-slide-to="${i}" ${i===0? 'class="active" aria-current="true"':''} aria-label="Slide ${i+1}"></button>`;
    inner += `
      <div class="carousel-item ${i===0? 'active':''}">
        <div class="ratio ratio-16x9">
          <iframe src="https://www.youtube.com/embed/${v.id}" title="${escapeHtml(v.title)}" allowfullscreen></iframe>
        </div>
        <div class="mt-2">
          <h5>${escapeHtml(v.title)}</h5>
          <p class="small text-muted">${escapeHtml(v.description || '')}</p>
        </div>
      </div>
    `;
  });

  indicators += '</div>';
  inner += '</div>';

  const controls = `
    <button class="carousel-control-prev" type="button" data-bs-target="#${id}" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#${id}" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  `;

  return `<div id="${id}" class="carousel slide" data-bs-ride="carousel">${indicators}${inner}${controls}</div>`;
}

// Event listener for the Search button
document.getElementById('searchBtn').addEventListener('click', async () => {
  const q = document.getElementById('queryInput').value.trim();
  if (!q) return alert('Please enter a query');
  const container = document.getElementById('carouselContainer');
  container.innerHTML = '<p>Loading...</p>';
  const data = await fetchVideos(q);
  if (data.error) {
    container.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
    return;
  }
  container.innerHTML = buildCarousel(data.videos);
});
