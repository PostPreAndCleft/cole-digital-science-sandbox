(() => {
  const grid = document.getElementById("video-grid");
  const pickCount = document.getElementById("pick-count");
  const refreshButton = document.getElementById("refresh-picks");

  if (!grid || !pickCount || !refreshButton) {
    return;
  }

  const parseCsv = (text) => {
    const rows = [];
    let row = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < text.length; i += 1) {
      const char = text[i];
      const next = text[i + 1];

      if (char === "\"" && next === "\"") {
        current += "\"";
        i += 1;
        continue;
      }

      if (char === "\"") {
        inQuotes = !inQuotes;
        continue;
      }

      if (char === "," && !inQuotes) {
        row.push(current);
        current = "";
        continue;
      }

      if ((char === "\n" || char === "\r") && !inQuotes) {
        if (current.length || row.length) {
          row.push(current);
          rows.push(row);
          row = [];
          current = "";
        }
        continue;
      }

      current += char;
    }

    if (current.length || row.length) {
      row.push(current);
      rows.push(row);
    }

    return rows;
  };

  const getVideoId = (url) => {
    if (!url) {
      return "";
    }

    const shortMatch = url.match(/youtu\.be\/([\w-]+)/);
    if (shortMatch) {
      return shortMatch[1];
    }

    const watchMatch = url.match(/[?&]v=([^&]+)/);
    if (watchMatch) {
      return watchMatch[1];
    }

    const liveMatch = url.match(/youtube\.com\/live\/([\w-]+)/);
    if (liveMatch) {
      return liveMatch[1];
    }

    return "";
  };

  const shuffle = (items) => {
    const array = [...items];
    for (let i = array.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  };

  const renderVideos = (videos, count) => {
    const picks = shuffle(videos).slice(0, count);
    grid.innerHTML = "";

    picks.forEach((video) => {
      const videoId = getVideoId(video.url);
      const card = document.createElement("article");
      card.className = "video-card";

      const thumb = document.createElement("img");
      thumb.className = "video-thumb";
      if (videoId) {
        thumb.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        thumb.alt = video.title ? `Thumbnail for ${video.title}` : "Video thumbnail";
      } else {
        thumb.alt = "Video thumbnail";
      }

      const title = document.createElement("h3");
      title.textContent = video.title || "Seminar talk";

      const meta = document.createElement("p");
      meta.className = "video-meta";
      meta.textContent = [video.speaker, video.affiliation].filter(Boolean).join(" · ");

      const date = document.createElement("p");
      date.className = "video-meta";
      date.textContent = video.date ? `Date: ${video.date}` : "";

      const link = document.createElement("a");
      link.className = "video-link";
      link.href = video.url;
      link.textContent = "Watch on YouTube →";

      card.appendChild(thumb);
      card.appendChild(title);
      if (meta.textContent) {
        card.appendChild(meta);
      }
      if (date.textContent) {
        card.appendChild(date);
      }
      card.appendChild(link);
      grid.appendChild(card);
    });
  };

  const setupControls = (videos) => {
    const count = Number.parseInt(pickCount.value, 10) || 6;
    renderVideos(videos, count);

    refreshButton.addEventListener("click", () => {
      const updatedCount = Number.parseInt(pickCount.value, 10) || 6;
      renderVideos(videos, updatedCount);
    });

    pickCount.addEventListener("change", () => {
      const updatedCount = Number.parseInt(pickCount.value, 10) || 6;
      renderVideos(videos, updatedCount);
    });
  };

  const loadVideos = async () => {
    if (Array.isArray(window.FARS_PLAYLIST_VIDEOS) && window.FARS_PLAYLIST_VIDEOS.length) {
      setupControls(window.FARS_PLAYLIST_VIDEOS);
      return;
    }

    const response = await fetch("assets/fars_playlist_videos.csv");
    const text = await response.text();
    const rows = parseCsv(text);
    const headers = rows.shift().map((header) => header.trim().toLowerCase());

    const videos = rows
      .map((row) => {
        const record = {};
        headers.forEach((header, index) => {
          record[header] = (row[index] || "").trim();
        });
        return record;
      })
      .filter((record) => record.url);

    setupControls(videos);
  };

  loadVideos().catch(() => {
    grid.textContent = "Unable to load the playlist. Please refresh the page.";
  });
})();
