// Sidebar: top-level sections that have children (i.e. "Documentation")
// start out expanded on every page, including Home.
//
// just-the-docs only expands a section when the current page is inside it,
// so on the homepage the section list was hidden behind a collapsed
// "Documentation".  This marks the top-level items "active" the same way
// the theme's own expander button does, so the button still works to
// collapse them.

document.addEventListener('DOMContentLoaded', function () {
  var items = document.querySelectorAll('#site-nav > .nav-list > .nav-list-item');
  items.forEach(function (item) {
    var expander = item.querySelector(':scope > .nav-list-expander');
    if (!expander) return;  // no children, nothing to expand
    item.classList.add('active');
    expander.setAttribute('aria-pressed', 'true');
  });
});
