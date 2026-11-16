// Sidebar: top-level sections that have children (i.e. "Documentation")
// start out expanded on every page, including Home.  So does "Concepts",
// one level down, since the concept pages are the heart of the site.
//
// just-the-docs only expands a section when the current page is inside it,
// so on the homepage the section list was hidden behind a collapsed
// "Documentation".  This marks the items "active" the same way the theme's
// own expander button does, so the button still works to collapse them.

document.addEventListener('DOMContentLoaded', function () {
  function expand(item) {
    var expander = item.querySelector(':scope > .nav-list-expander');
    if (!expander) return;  // no children, nothing to expand
    item.classList.add('active');
    expander.setAttribute('aria-pressed', 'true');
  }

  var top = document.querySelectorAll('#site-nav > .nav-list > .nav-list-item');
  top.forEach(expand);

  var links = document.querySelectorAll('#site-nav .nav-list-link');
  links.forEach(function (link) {
    var path = link.getAttribute('href') || '';
    if (/\/docs\/concepts\/?$/.test(path))
      expand(link.closest('.nav-list-item'));
  });
});
