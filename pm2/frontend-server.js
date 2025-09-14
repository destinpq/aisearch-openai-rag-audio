// Minimal static server using Node builtin modules (no external deps).
const http = require("http");
const fs = require("fs");
const path = require("path");
const url = require("url");

const port = parseInt(process.env.PORT || "45532", 10);
const staticDir = path.resolve(
  process.env.STATIC_DIR || path.join(__dirname, "..", "backend", "static")
);

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.statusCode = 404;
      res.end("Not found");
      return;
    }
    res.statusCode = 200;
    // very small mime mapping
    if (filePath.endsWith(".html"))
      res.setHeader("Content-Type", "text/html; charset=utf-8");
    else if (filePath.endsWith(".js"))
      res.setHeader("Content-Type", "application/javascript");
    else if (filePath.endsWith(".css"))
      res.setHeader("Content-Type", "text/css");
    else if (filePath.endsWith(".json"))
      res.setHeader("Content-Type", "application/json");
    else if (filePath.endsWith(".png"))
      res.setHeader("Content-Type", "image/png");
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url);
  let filePath = path.join(staticDir, parsed.pathname);
  // if path is directory or root, serve index.html
  if (parsed.pathname === "/" || parsed.pathname.endsWith("/")) {
    filePath = path.join(staticDir, "index.html");
  }
  // normalize & prevent directory traversal
  if (!filePath.startsWith(staticDir)) {
    res.statusCode = 403;
    res.end("Forbidden");
    return;
  }
  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // fallback to index.html for SPA
      const fallback = path.join(staticDir, "index.html");
      return sendFile(res, fallback);
    }
    sendFile(res, filePath);
  });
});

server.listen(port, "127.0.0.1", () => {
  console.log(
    `Static server listening on 127.0.0.1:${port}, serving ${staticDir}`
  );
});
