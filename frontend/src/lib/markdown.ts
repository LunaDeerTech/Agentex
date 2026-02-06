/**
 * Markdown Renderer Utility
 *
 * Provides markdown-it based rendering with syntax highlighting support
 * and safe HTML output for chat messages.
 */

import MarkdownIt from 'markdown-it'

// Create markdown-it instance with optimized settings for chat
const md = new MarkdownIt({
  html: false, // Disable HTML tags for security
  xhtmlOut: false,
  breaks: true, // Convert \n to <br>
  linkify: true, // Auto-detect URLs
  typographer: true // Smart quotes and other typographic replacements
})

// Add target="_blank" to all links
const defaultRender =
  md.renderer.rules.link_open ||
  function (tokens, idx, options, _env, self) {
    return self.renderToken(tokens, idx, options)
  }

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  const token = tokens[idx]
  if (!token) return defaultRender(tokens, idx, options, env, self)

  // Add target="_blank" and rel attributes
  const aIndex = token.attrIndex('target')
  if (aIndex < 0) {
    token.attrPush(['target', '_blank'])
  } else if (token.attrs && token.attrs[aIndex]) {
    token.attrs[aIndex][1] = '_blank'
  }

  const relIndex = token.attrIndex('rel')
  if (relIndex < 0) {
    token.attrPush(['rel', 'noopener noreferrer'])
  }

  return defaultRender(tokens, idx, options, env, self)
}

// Custom code block renderer with language class
md.renderer.rules.fence = function (tokens, idx, _options, _env, _self) {
  const token = tokens[idx]
  if (!token) return ''

  const info = token.info ? token.info.trim() : ''
  const lang = info.split(/\s+/g)[0] || 'text'
  const code = token.content

  // Return custom code block HTML
  return `<pre class="code-block language-${lang}"><code class="language-${lang}">${md.utils.escapeHtml(code)}</code></pre>`
}

/**
 * Render markdown content to HTML
 * @param content - Markdown string to render
 * @returns Rendered HTML string
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''
  return md.render(content)
}

/**
 * Render markdown inline (no paragraph wrapping)
 * @param content - Markdown string to render
 * @returns Rendered HTML string without paragraph tags
 */
export function renderMarkdownInline(content: string): string {
  if (!content) return ''
  return md.renderInline(content)
}

/**
 * Escape HTML special characters
 * @param text - Text to escape
 * @returns Escaped text
 */
export function escapeHtml(text: string): string {
  return md.utils.escapeHtml(text)
}

export default md
