//
// File: %revolt-console.js
//
//=============================================================================//
//
// Marks up console transcripts in Rebol blocks (``` or ```rebol) so they read like a
// terminal: input lines (>>) bright, results (==) dimmer, errors (**) in
// between, with the prompt glyphs and ; comments receding.  The classes
// (rc-in, rc-out, rc-err, rc-txt, rc-mark, rc-cmt) are styled in
// _sass/custom/custom.scss.
//
// Only blocks whose first line is a prompt are touched, and only when the
// highlighter left the code as plain text (no <span>s), which is the case
// for Rebol since Rouge has no lexer for it.  Without this script, or with
// JavaScript off, the blocks are plain light-on-dark text.
//
// Also: when Rouge has no lexer, kramdown emits a bare <pre><code> instead
// of the <div class="highlighter-rouge"><div class="highlight"><pre> nest
// that just-the-docs styles and adds its copy button to.  This script is
// loaded with `defer`, so it runs before the theme's DOMContentLoaded
// handlers; it rebuilds bare blocks into that structure first.
//
// And: a block right after a `<!-- doctest: negative-test -->` comment is an
// example that's supposed to fail.  kramdown keeps the comment in the page,
// so the block after it gets the class `revolt-fails`, which custom.scss
// draws with a red border and an "Error" tab.
//

(function () {
  "use strict";

  function lineClass(line) {
    if (line.startsWith(">>")) return "rc-in";
    if (line.startsWith("==")) return "rc-out";
    if (line.startsWith("**")) return "rc-err";
    return "rc-txt";
  }

  // Splits "text ; comment" so the comment can be dimmed.  A ; inside a
  // string would be misread, but transcripts rarely have one, and the cost
  // is only a cosmetic shade.
  function splitComment(text) {
    var m = /^(.*?)(\s;.*|^;.*)$/.exec(text);
    if (!m) return [text, null];
    return [m[1], m[2]];
  }

  function span(cls, text) {
    var s = document.createElement("span");
    s.className = cls;
    s.textContent = text;
    return s;
  }

  function decorate(code) {
    if (code.children.length !== 0) return; // a lexer already marked it up
    var text = code.textContent;
    var lines = text.split("\n");
    var first = lines.find(function (l) { return l.trim() !== ""; });
    if (!first || !first.startsWith(">>")) return;

    var frag = document.createDocumentFragment();
    lines.forEach(function (line, i) {
      if (line !== "") {
        var cls = lineClass(line);
        var wrap = span(cls, "");
        var rest = line;
        if (cls !== "rc-txt") {
          wrap.appendChild(span("rc-mark", line.slice(0, 2)));
          rest = line.slice(2);
        }
        var parts = splitComment(rest);
        wrap.appendChild(document.createTextNode(parts[0]));
        if (parts[1] !== null) wrap.appendChild(span("rc-cmt", parts[1]));
        frag.appendChild(wrap);
      }
      if (i < lines.length - 1) frag.appendChild(document.createTextNode("\n"));
    });
    code.textContent = "";
    code.appendChild(frag);
  }

  // <pre><code class="language-x"> (not already inside a wrapper) becomes
  // <div class="language-x highlighter-rouge"><div class="highlight">
  // <pre class="highlight"><code>, as kramdown would have produced with a
  // lexer.
  function wrap(code) {
    var pre = code.parentNode;
    if (!pre || pre.tagName !== "PRE") return;
    if (pre.parentNode.closest(".highlighter-rouge, figure.highlight")) return;
    var m = /(?:^|\s)language-([\w-]+)/.exec(code.className);
    var outer = document.createElement("div");
    outer.className = (m ? "language-" + m[1] + " " : "") + "highlighter-rouge";
    var inner = document.createElement("div");
    inner.className = "highlight";
    pre.parentNode.insertBefore(outer, pre);
    outer.appendChild(inner);
    inner.appendChild(pre);
    pre.className = "highlight";
  }

  // A fenced block with no language named is Rebol.  Depending on the
  // kramdown and Rouge versions, such a block comes out either with no class
  // at all, or highlighted as `language-plaintext` (GitHub Pages does the
  // latter).  Either way, name it Rebol here.  A block that *asks* for plain
  // text says ```text, which comes out as `language-text` and is left alone.
  function defaultToRebol(code) {
    if (code.parentNode.closest(".highlighter-rouge, figure.highlight")) return;
    code.classList.add("language-rebol");
  }

  function plaintextToRebol(outer) {
    outer.classList.remove("language-plaintext");
    outer.classList.add("language-rebol");
  }

  // Mark the block after each negative-test comment (see top of file).
  function markFailing() {
    var main = document.querySelector(".main-content") || document.body;
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_COMMENT);
    var comment;
    while ((comment = walker.nextNode())) {
      if (!/^\s*doctest:\s*negative-test\b/.test(comment.nodeValue)) continue;
      var el = comment.nextElementSibling || nextElementAfter(comment);
      if (el && el.matches(".highlighter-rouge, figure.highlight"))
        el.classList.add("revolt-fails");
    }
  }

  function nextElementAfter(node) {
    var n = node.nextSibling;
    while (n && n.nodeType !== 1) n = n.nextSibling;
    return n;
  }

  function run() {
    document.querySelectorAll("div.language-plaintext.highlighter-rouge").forEach(plaintextToRebol);
    document.querySelectorAll("pre > code:not([class*='language-'])").forEach(defaultToRebol);
    document.querySelectorAll("pre > code[class*='language-']").forEach(wrap);
    markFailing();
    document.querySelectorAll("div.language-rebol pre code").forEach(decorate);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
