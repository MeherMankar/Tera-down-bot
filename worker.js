export default {
  async fetch(req, env, ctx) {
    try {
      const url = new URL(req.url);
      const src = url.searchParams.get("src");
      if (!src) return bad(400, "Missing ?src=<https-url>");

      let srcUrl;
      try { srcUrl = new URL(src); } catch { return bad(400, "Invalid src URL"); }
      if (srcUrl.protocol !== "https:") return bad(400, "Only https URLs are allowed");

      const teraboxHosts = new Set([
        "terabox.com", "www.terabox.com", "1024terabox.com", "www.1024terabox.com",
        "teraboxapp.com", "www.teraboxapp.com"
      ]);

      if (teraboxHosts.has(srcUrl.hostname)) {
        return await handleTerabox(srcUrl, req, env, ctx);
      }

      // Regular file proxy for non-Terabox URLs
      const allowed = (env.ALLOW_HOSTS || "").split(",").map(h => h.trim().toLowerCase()).filter(Boolean);
      if (!allowed.includes(srcUrl.hostname.toLowerCase())) {
        return bad(403, "Host not on allowlist");
      }

      const range = req.headers.get("range") || "";
      const upstream = await fetch(srcUrl.toString(), {
        method: "GET",
        headers: range ? { range } : undefined,
        redirect: "follow"
      });

      if (!(upstream.ok || upstream.status === 206)) {
        return bad(502, `Upstream error: ${upstream.status}`);
      }

      return new Response(upstream.body, {
        status: upstream.status,
        headers: filterHeaders(upstream.headers)
      });

    } catch (e) {
      console.error('Worker error:', e);
      return bad(500, `Server error: ${e?.message || 'Unknown error'}`);
    }
  }
};

async function handleTerabox(srcUrl, req, env, ctx) {
  try {
    // Extract file ID from Terabox URL
    const fileId = extractTeraboxId(srcUrl.toString());
    if (!fileId) return bad(400, "Invalid Terabox URL");

    // Try to get direct download link
    const downloadUrl = await getTeraboxDownloadUrl(fileId, srcUrl.toString());
    if (!downloadUrl) return bad(404, "Could not extract download URL");

    // Proxy the actual file
    const range = req.headers.get("range") || "";
    const upstream = await fetch(downloadUrl, {
      method: "GET",
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.terabox.com/",
        ...(range ? { range } : {})
      },
      redirect: "follow"
    });

    if (!(upstream.ok || upstream.status === 206)) {
      return bad(502, `Download failed: ${upstream.status}`);
    }

    return new Response(upstream.body, {
      status: upstream.status,
      headers: filterHeaders(upstream.headers)
    });

  } catch (e) {
    console.error('Terabox error:', e);
    return bad(500, `Terabox error: ${e?.message || 'Unknown error'}`);
  }
}

function extractTeraboxId(url) {
  const patterns = [
    /\/s\/([a-zA-Z0-9_-]+)/,
    /surl=([a-zA-Z0-9_-]+)/,
    /uk=(\d+).*?shareid=(\d+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1] || `${match[1]}_${match[2]}`;
  }
  return null;
}

async function getTeraboxDownloadUrl(fileId, originalUrl) {
  try {
    // Method 1: Try API endpoint
    const apiUrl = `https://www.terabox.com/api/shorturlinfo?shorturl=${fileId}&root=1`;
    const response = await fetch(apiUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.terabox.com/",
        "Accept": "application/json"
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data?.list?.[0]?.dlink) {
        return data.list[0].dlink;
      }
    }

    // Method 2: Parse HTML page
    const pageResponse = await fetch(originalUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    });

    if (pageResponse.ok) {
      const html = await pageResponse.text();
      
      // Extract download URL from various possible locations
      const patterns = [
        /"dlink":"([^"]+)"/,
        /dlink["']?:["']?([^"',\s}]+)/,
        /download[Uu]rl["']?:["']?([^"',\s}]+)/
      ];
      
      for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match && match[1]) {
          return match[1].replace(/\\u002F/g, "/").replace(/\\/g, "");
        }
      }
    }

    return null;
  } catch (e) {
    console.error('Download URL extraction error:', e);
    return null;
  }
}

function bad(code, msg) {
  return new Response(JSON.stringify({ error: msg }), {
    status: code,
    headers: { "content-type": "application/json; charset=utf-8" }
  });
}

function filterHeaders(src) {
  const h = new Headers();
  const allow = new Set([
    "content-type", "content-length", "content-disposition", "accept-ranges",
    "etag", "last-modified", "cache-control", "expires", "date", "vary", "content-range"
  ]);
  
  for (const [k, v] of src.entries()) {
    const key = k.toLowerCase();
    if (allow.has(key)) h.set(key, v);
  }
  
  if (!h.has("content-disposition")) {
    h.set("content-disposition", "inline");
  }
  h.set("access-control-allow-origin", "*");
  return h;
}