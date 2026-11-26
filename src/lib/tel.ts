// Escape plain text, then make the phone numbers tappable. Use with set:html.
export function telify(s: string): string {
  const esc = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  return esc
    .replace(/0151 558 0334/g, '<a href="tel:01515580334">0151 558 0334</a>')
    .replace(/0800 111 999/g, '<a href="tel:08001119999">0800 111 999</a>');
}
