// The pencil "Edit page" link: _includes/components/breadcrumbs.html puts it
// at the right end of the breadcrumb row, which works without JavaScript.
// This moves it next to the page's title, wiki style, as a small "Edit" chip.
//
// Most pages write their title as `# Title` in Markdown, so there's no layout
// that could render the chip beside it; the title is found here instead.
// (Datatype and native pages render their <h1> from a layout, and are
// handled the same way.)
//
// head_custom.html sets the `revolt-js` class on <html> before the page
// draws, and the CSS keeps the link hidden in the breadcrumb row while that
// class is set, so it doesn't flash there first.  If no title is found, the
// link is shown where it is.

document.addEventListener('DOMContentLoaded', function () {
  var link = document.getElementById('revolt-edit');
  if (!link) return;

  var title = document.querySelector('#main-content main h1');
  var visible = title && title.getClientRects().length > 0
    && !title.classList.contains('revolt-visually-hidden');

  if (visible) {
    var row = document.createElement('div');
    row.className = 'revolt-title-row';
    title.parentNode.insertBefore(row, title);
    row.appendChild(title);
    row.appendChild(link);
    link.classList.add('revolt-edit-chip');
  }

  document.documentElement.classList.add('revolt-edit-placed');
});
