// Sidebar: "Concepts" starts out expanded on every page, including Home,
// since the concept pages are the heart of the site.  Inside the PARSE
// universe, its own Concepts and Combinators start out expanded the same
// way.
//
// just-the-docs only expands a section when the current page is inside it.
// This marks the item "active" the same way the theme's own expander button
// does, so the button still works to collapse it.

document.addEventListener('DOMContentLoaded', function () {
  function expand(item) {
    var expander = item.querySelector(':scope > .nav-list-expander');
    if (!expander) return;  // no children, nothing to expand
    item.classList.add('active');
    expander.setAttribute('aria-pressed', 'true');
  }

  var links = document.querySelectorAll('#site-nav .nav-list-link');
  links.forEach(function (link) {
    var path = link.getAttribute('href') || '';
    if (/\/docs\/(dialects\/parse\/)?concepts\/?$/.test(path)
        || /\/docs\/dialects\/parse\/combinators\/?$/.test(path))
      expand(link.closest('.nav-list-item'));
  });
});
