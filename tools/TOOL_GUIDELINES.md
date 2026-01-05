# Tool Development Guidelines for xav.ai/tools

This document provides guidelines for building new tools for the xav.ai/tools collection. These guidelines are designed to be used by both human developers and AI assistants (LLMs).

## Core Principles

1. **Static HTML/JS Only** - No build steps, no frameworks, no server-side processing
2. **Privacy-First** - All processing happens client-side; no data leaves the browser
3. **Mobile-Friendly** - Responsive design that works on all screen sizes
4. **Accessible** - Follows WCAG guidelines, supports keyboard navigation
5. **Consistent** - Matches the xav.ai design language

## File Structure

Each tool should have its own directory:

```
/tools/
├── index.html              # Tools landing page
├── TOOL_GUIDELINES.md      # This file
└── [tool-name]/
    ├── index.html          # Main tool page
    └── [optional assets]   # Images, additional JS if needed
```

## HTML Template

Use this as a starting point for any new tool:

```html
<!DOCTYPE HTML>
<html>
<head>
    <title>[Tool Name] - Xav Kearney</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <!-- Favicons -->
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="#ffffff">

    <!-- SEO -->
    <meta name="author" content="Xav Kearney">
    <meta name="description" content="[Brief tool description]">
    <meta property="og:title" content="[Tool Name] - Xav Kearney">
    <meta property="og:description" content="[Brief tool description]">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://xav.ai/tools/[tool-name]/">
    <link rel="canonical" href="https://xav.ai/tools/[tool-name]/">

    <!-- Fonts & Shared CSS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/shared.css">

    <style>
        /* Tool-specific styles go here */
        .back-link {
            margin-bottom: 2rem;
            font-size: clamp(0.9rem, 2.5vw, 1rem);
        }
    </style>
</head>
<body>
    <!-- Theme Toggle (required) -->
    <div class="theme-toggle">
        <span class="sun">&#9728;</span>
        <button class="toggle-switch" aria-label="Toggle dark mode"></button>
        <span class="moon">&#9790;</span>
    </div>

    <!-- Google Analytics (GA4) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-CF2279ZMGC"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-CF2279ZMGC');
    </script>

    <header>
        <p class="back-link"><a href="/tools/">&larr; Back to Tools</a></p>
        <h1>[Tool Name]</h1>
    </header>

    <main>
        <!-- Tool content goes here -->
    </main>

    <!-- Theme Toggle Script (required) -->
    <script>
        (function () {
            const toggle = document.querySelector('.toggle-switch');
            const sunIcon = document.querySelector('.sun');
            const moonIcon = document.querySelector('.moon');
            const themeColorMeta = document.querySelector('meta[name="theme-color"]');

            function getSystemTheme() {
                return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }

            function getEffectiveTheme() {
                const saved = localStorage.getItem('theme');
                return saved || getSystemTheme();
            }

            function updateIcons(theme) {
                if (theme === 'dark') {
                    sunIcon.classList.remove('active');
                    moonIcon.classList.add('active');
                } else {
                    sunIcon.classList.add('active');
                    moonIcon.classList.remove('active');
                }
            }

            function updateThemeColor(theme) {
                themeColorMeta.setAttribute('content', theme === 'dark' ? '#1a1a1a' : '#ffffff');
            }

            function applyTheme(theme) {
                document.documentElement.setAttribute('data-theme', theme);
                updateIcons(theme);
                updateThemeColor(theme);
            }

            applyTheme(getEffectiveTheme());

            toggle.addEventListener('click', function () {
                const current = document.documentElement.getAttribute('data-theme') || getSystemTheme();
                const next = current === 'dark' ? 'light' : 'dark';
                localStorage.setItem('theme', next);
                applyTheme(next);
            });

            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
                if (!localStorage.getItem('theme')) {
                    applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        })();
    </script>

    <!-- Tool-specific JavaScript -->
    <script>
        // Tool logic goes here
    </script>
</body>
</html>
```

## Design Specifications

### Colors (use CSS variables)

| Variable | Light Mode | Dark Mode | Usage |
|----------|------------|-----------|-------|
| `--bg` | #fff | #1a1a1a | Background |
| `--text` | #111 | #eee | Primary text |
| `--text-muted` | #666 | #999 | Secondary text |
| `--link-underline` | #999 | #666 | Link underline |
| `--link-underline-hover` | #111 | #eee | Link underline on hover |
| `--toggle-bg` | #e0e0e0 | #444 | Toggle background |
| `--toggle-knob` | #fff | #1a1a1a | Toggle knob |

Accent color for selections: `rgba(167, 139, 250, 0.3)` (purple)

### Typography

- **Font**: Source Sans Pro, weight 300
- **Body text**: `clamp(1.1rem, 3vw, 1.35rem)`
- **H1**: `clamp(2.5rem, 8vw, 4rem)`
- **H2**: `clamp(1.5rem, 5vw, 2rem)`
- **Small text**: `clamp(0.9rem, 2.5vw, 1rem)`
- **Line height**: 1.7

### Layout

- **Max content width**: 650px
- **Padding**: `clamp(1.5rem, 5vw, 4rem)`
- **Center content** with flexbox (`display: flex; flex-direction: column; align-items: center;`)

### Interactive Elements

**Buttons:**
```css
.btn {
    background: var(--text);
    color: var(--bg);
    border: none;
    padding: 0.75rem 1.5rem;
    font-family: inherit;
    font-size: 1rem;
    font-weight: 300;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.btn:active {
    transform: translateY(0);
}

.btn:focus {
    outline: 2px solid var(--link-underline-hover);
    outline-offset: 3px;
}

.btn:focus:not(:focus-visible) {
    outline: none;
}
```

**Secondary/outline buttons:**
```css
.btn-secondary {
    background: transparent;
    color: var(--text);
    border: 1px solid var(--link-underline);
}

.btn-secondary:hover {
    border-color: var(--link-underline-hover);
}
```

**Inputs:**
```css
input,
textarea,
select {
    font-family: inherit;
    font-size: 1rem;
    font-weight: 300;
    padding: 0.75rem;
    border: 1px solid var(--link-underline);
    border-radius: 4px;
    background: var(--bg);
    color: var(--text);
    width: 100%;
    transition: border-color 0.2s ease;
}

input:focus,
textarea:focus,
select:focus {
    outline: none;
    border-color: var(--link-underline-hover);
}

input::placeholder,
textarea::placeholder {
    color: var(--text-muted);
}
```

**Labels:**
```css
label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: clamp(0.95rem, 2.5vw, 1.1rem);
    color: var(--text-muted);
}
```

## Data Persistence

Use localStorage for saving user preferences or data:

```javascript
// Save data
localStorage.setItem('toolName_key', JSON.stringify(data));

// Load data
const data = JSON.parse(localStorage.getItem('toolName_key')) || defaultValue;

// Clear data
localStorage.removeItem('toolName_key');
```

**Key naming convention:** `toolName_settingName` (e.g., `timer_duration`, `converter_lastUnit`)

## Accessibility Requirements

1. All interactive elements must be keyboard accessible
2. Use semantic HTML (`<button>`, `<input>`, `<label>`, `<main>`, `<header>`, etc.)
3. Include `aria-label` for icon-only buttons
4. Ensure color contrast meets WCAG AA standards (4.5:1 for text)
5. Respect `prefers-reduced-motion` for animations
6. Include visible focus states for all interactive elements
7. Associate labels with form inputs using `for` and `id` attributes

## Mobile Considerations

1. Touch targets should be at least 44x44px
2. Test at 320px viewport width minimum
3. Use `clamp()` for responsive sizing
4. Avoid hover-only interactions (provide tap alternatives)
5. Consider thumb-friendly placement of key actions (bottom of screen)
6. Test on actual mobile devices, not just browser dev tools

## Performance Guidelines

1. No external dependencies (no jQuery, React, Vue, etc.)
2. Use the shared.css stylesheet - don't duplicate base styles
3. Minimize JavaScript; vanilla JS only
4. Lazy load non-critical resources if needed
5. Optimize any images (use SVG where possible, compress PNGs/JPGs)
6. Keep total page size under 100KB where possible

## Adding a New Tool to the Index

After creating your tool, add an entry to `/tools/index.html`:

1. Remove or comment out the empty state message
2. Add a new list item:

```html
<li class="tool-item">
    <a href="/tools/[tool-name]/" class="tool-name">[Tool Name]</a>
    <p class="tool-description">[Brief description - one sentence]</p>
</li>
```

## Testing Checklist

Before considering a tool complete:

- [ ] Works on mobile (320px width minimum)
- [ ] Works on desktop (test at various widths)
- [ ] Light theme displays correctly
- [ ] Dark theme displays correctly
- [ ] Theme toggle works and persists across page refresh
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus states are visible
- [ ] localStorage (if used) works correctly
- [ ] No console errors
- [ ] Page loads quickly (under 1 second)

## Example Tool Ideas

Tools that fit well with this format:

- **Converters**: Temperature, length, weight, currency, time zones
- **Text utilities**: Word count, character count, case converter, JSON formatter/validator
- **Time tools**: Countdown timer, pomodoro timer, stopwatch, time zone converter
- **Color tools**: Color picker, contrast checker, palette generator
- **Calculators**: Tip calculator, percentage calculator, compound interest
- **Generators**: UUID generator, password generator, lorem ipsum
- **Encoders/Decoders**: Base64, URL encode/decode, HTML entities

## Questions?

If you're an LLM building a tool and have questions about these guidelines, prioritize:
1. Simplicity over features
2. Mobile-friendliness
3. Accessibility
4. Consistency with the existing design language

When in doubt, keep it simple. A tool that does one thing well is better than a complex tool that's hard to use.
