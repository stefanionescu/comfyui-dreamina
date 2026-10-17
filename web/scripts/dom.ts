/**
 * Create a typed element and insert optional text safely.
 * @param tag - The HTML tag to create.
 * @param text - Plain text content, if needed.
 * @returns The new element.
 */
export function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  text?: string,
): HTMLElementTagNameMap[K] {
  // reason: Callers supply literal UI tags; content becomes a Text node, never parsed HTML.
  // bearer:disable javascript_lang_dangerous_insert_html
  const node = document.createElement(tag);
  if (text !== undefined) node.appendChild(document.createTextNode(text));
  return node;
}

/**
 * Create a button with an explicit form behavior.
 * @param text - The visible button label.
 * @param type - Whether the button submits its form.
 * @returns The new button.
 */
export function button(text: string, type: 'button' | 'submit' = 'button'): HTMLButtonElement {
  const node = element('button', text);
  node.type = type;
  return node;
}

/**
 * Create a link that opens a checked https address in a new tab, with no access back to this page.
 * @param text - The visible link text.
 * @param url - An https address the reply schema already checked.
 * @returns The new link.
 */
export function externalLink(text: string, url: string): HTMLAnchorElement {
  const node = element('a', text);
  node.href = url;
  node.target = '_blank';
  node.rel = 'noopener noreferrer';
  return node;
}
