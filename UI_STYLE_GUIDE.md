# THINKedIn UI Style Guide

A comprehensive design system for maintaining consistent UI across the application.

---

## Color Palette

### Primary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary Blue | `#4075C9` | `rgb(64, 117, 201)` | Accents, hover states, highlights, glows |
| Grey | `#C4BFC0` | `rgb(196, 191, 192)` | Secondary text, labels, borders |
| White | `#FFFFFF` | `rgb(255, 255, 255)` | Primary text, headings |

### Background Colors
| Name | Hex | Usage |
|------|-----|-------|
| Background Dark | `#030305` | Primary background |
| Background Mid | `#08080f` | Gradient midpoint |
| Background Light | `#050508` | Gradient endpoint |

### Background Gradient
```css
background: linear-gradient(135deg, #030305 0%, #08080f 50%, #050508 100%);
```

### Opacity Variants
| Element | Opacity |
|---------|---------|
| Primary Blue (subtle) | `rgba(64, 117, 201, 0.1)` - `rgba(64, 117, 201, 0.15)` |
| Primary Blue (hover) | `rgba(64, 117, 201, 0.3)` |
| Grey borders | `rgba(196, 191, 192, 0.3)` - `rgba(196, 191, 192, 0.4)` |
| Light rays | `rgba(64, 117, 201, 0.08)` |

---

## Typography

### Font Families
```css
/* Display/Headings - Elegant serif */
font-family: 'Playfair Display', serif;

/* Body/UI - Clean sans-serif */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Font Import
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
```

### Type Scale
| Element | Font | Size | Weight | Letter Spacing | Color |
|---------|------|------|--------|----------------|-------|
| Hero Title | Playfair Display | 72px | 400 | normal | `#FFFFFF` |
| Section Title | Playfair Display | 48px | 400 | normal | `#FFFFFF` |
| Labels (uppercase) | Inter | 12px | 500 | 0.3em | `#C4BFC0` |
| Feature Title | Inter | 14px | 600 | 0.15em | `#FFFFFF` |
| Body Text | Inter | 15px | 300 | normal | `#C4BFC0` |
| Small Text | Inter | 14px | 300 | normal | `#C4BFC0` |
| Button Text | Inter | 14px | 500 | normal | `#FFFFFF` |
| Nav Text | Inter | 14px | 500 | normal | `#C4BFC0` |

---

## Spacing System

### Base Unit: 4px

| Name | Value | Usage |
|------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Small gaps |
| md | 12px | Icon gaps |
| lg | 16px | Standard spacing |
| xl | 24px | Section spacing |
| 2xl | 32px | Large gaps |
| 3xl | 40px | Major sections |
| 4xl | 60px | Page padding |

### Page Padding
- Desktop: `60px` horizontal
- Tablet: `40px` horizontal
- Mobile: `24px` horizontal

---

## Components

### Buttons

#### Primary CTA Button
```css
.btn-primary {
  background: transparent;
  border: 1px solid rgba(196, 191, 192, 0.4);
  color: #ffffff;
  padding: 14px 32px;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: rgba(64, 117, 201, 0.15);
  border-color: #4075C9;
  box-shadow: 0 4px 20px rgba(64, 117, 201, 0.2);
}
```

#### Nav Button
```css
.btn-nav {
  background: transparent;
  border: 1px solid rgba(196, 191, 192, 0.3);
  color: #C4BFC0;
  padding: 10px 24px;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-nav:hover {
  background: rgba(64, 117, 201, 0.1);
  border-color: #4075C9;
  color: #fff;
}
```

#### Icon Button (Arrow)
```css
.btn-icon {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(196, 191, 192, 0.3);
  background: transparent;
  color: #C4BFC0;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  border-color: #4075C9;
  color: #fff;
  background: rgba(64, 117, 201, 0.1);
}
```

### Dividers
```css
.divider {
  width: 40px;
  height: 2px;
  background: #C4BFC0;
}
```

---

## Effects & Animations

### Transitions
```css
/* Standard transition */
transition: all 0.3s ease;

/* Fade in */
transition: opacity 0.5s ease;
```

### Hover Transform
```css
transform: translateY(-2px); /* Subtle lift on hover */
```

### Box Shadows
```css
/* Blue glow - buttons */
box-shadow: 0 4px 20px rgba(64, 117, 201, 0.2);

/* Stronger blue glow */
box-shadow: 0 8px 24px rgba(64, 117, 201, 0.3);

/* 3D element shadow */
box-shadow:
  inset -30px -30px 60px rgba(0, 0, 0, 0.6),
  inset 20px 20px 40px rgba(64, 117, 201, 0.1),
  0 0 80px rgba(64, 117, 201, 0.2);
```

### Float Animation
```css
@keyframes float {
  0%, 100% {
    transform: translateY(0) rotateY(0deg);
  }
  50% {
    transform: translateY(-20px) rotateY(10deg);
  }
}

animation: float 8s ease-in-out infinite;
```

### Light Rays (Background Effect)
```css
.light-ray {
  position: absolute;
  background: linear-gradient(180deg, rgba(64, 117, 201, 0.08) 0%, transparent 100%);
  transform-origin: top left;
}

/* Ray 1 */
width: 600px;
height: 150%;
top: -20%;
left: -10%;
transform: rotate(25deg);

/* Ray 2 */
width: 400px;
height: 120%;
top: -10%;
left: 5%;
transform: rotate(35deg);
opacity: 0.5;
```

---

## Layout Principles

### Grid Structure
- Max content width: `1400px`
- Three-column layout for hero sections (left content, center visual, right content)
- Flexbox with `justify-content: space-between`

### Z-Index Scale
| Layer | Z-Index |
|-------|---------|
| Background effects | 0 |
| Content | 10 |
| Navigation | 100 |
| Modals/Overlays | 1000 |

---

## Responsive Breakpoints

```css
/* Large desktop */
@media (max-width: 1200px) { }

/* Tablet */
@media (max-width: 992px) { }

/* Mobile */
@media (max-width: 576px) { }
```

### Responsive Behavior
- **1200px+**: Full three-column layout
- **992px-1200px**: Reduced spacing, smaller visuals
- **Below 992px**: Stack to single column, center-aligned
- **Below 576px**: Compact padding, smaller text

---

## 3D Sphere Component

### Structure
8 layered divs creating depth illusion with:
- Radial gradients for base sphere
- Linear gradients for highlight layers
- Transform with `rotateX`, `rotateY`, `translateZ` for 3D effect
- Border-radius variations for organic shape

### Color Progression (darkest to lightest)
1. `#050a14` → `#0d1f3c` → `#1a3a6e` (base)
2. `rgba(64, 117, 201, 0.4)` (mid layers)
3. `rgba(135, 180, 255, 0.3)` (highlight layers)
4. `rgba(240, 248, 255, 0.2)` (brightest center)

---

## Glass UI Elements (Alternative Style)

For sections needing glass morphism:
```css
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}
```

---

## Icon Style

- Line icons preferred (stroke-based)
- Stroke width: `1.5px` - `2px`
- Color: `#C4BFC0` default, `#FFFFFF` on hover
- Sizes: 16px (small), 24px (medium), 36px (large), 60px (feature)

---

## Usage Notes

1. **Contrast**: Always ensure sufficient contrast between text and background
2. **Hover States**: All interactive elements must have hover feedback
3. **Consistency**: Use variables/CSS custom properties for colors
4. **Performance**: Limit complex animations on mobile
5. **Accessibility**: Maintain focus states for keyboard navigation

---

## CSS Custom Properties (Recommended)

```css
:root {
  /* Colors */
  --color-primary: #4075C9;
  --color-grey: #C4BFC0;
  --color-white: #FFFFFF;
  --color-bg-dark: #030305;
  --color-bg-mid: #08080f;
  --color-bg-light: #050508;

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;
  --spacing-2xl: 32px;
  --spacing-3xl: 40px;
  --spacing-4xl: 60px;

  /* Transitions */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 50%;
}
```
