"use strict";
/* Inject (or re-inject) the assembled library into the artifact.
   Usage: node inject_library.js library.json path/to/triton-rack.html */
const fs = require("fs");
const lib = fs.readFileSync(process.argv[2], "utf8").trim();
JSON.parse(lib); /* must be valid JSON */
if (/<\/|<script|<!--/i.test(lib)) throw new Error("library contains HTML-hostile sequences");
let html = fs.readFileSync(process.argv[3], "utf8");
const re = /const PHRASES=\[[^\n]*\];/;
if (!re.test(html)) throw new Error("PHRASES line not found");
html = html.replace(re, "const PHRASES=" + lib + ";");
fs.writeFileSync(process.argv[3], html);
console.log("injected", (lib.length / 1024).toFixed(1) + "KB");
