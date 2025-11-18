Amazing — let’s turn the PurdueTHINK site you screenshotted into **AI-ready mobile UI specs** (390×844 viewport, iOS + Android).
I’ll treat each major page/section as a “screen” to make generation clean and modular. I’ll also include a **persistent App Header** spec you can reuse across screens.

**Global tokens (use everywhere unless overridden)**

* **Color palette:**

  * Primary Blue: **#17D4D4**
  * Black: **#000000**
  * White: **#FFFFFF**
  * Off-white for long copy (optional): **#F5F7FA**
  * Divider (hairline): **rgba(255,255,255,0.12)**
* **Font:** Poppins (Regular, Medium, SemiBold, Bold)
* **Default tap area:** ≥44×44px
* **Default button radius:** 16px
* **Default card radius:** 20px
* **Shadow (iOS/Android):** 0 6 16 rgba(0,0,0,0.18), elevation 8
* **Safe areas:** Respect top/bottom safe insets; content anchored to a 24px system margin unless specified.

---

# App Header (Persistent / Reusable)

**Background:** Solid black **#000000**

**Layout:**

* Fixed height **72px**.
* Content area **left-aligned** within **24px** horizontal padding.
* **Grid:** 3 columns (Logo | Nav cluster | CTA). On mobile we show a compact row:

  * Left: Logo
  * Center: horizontal nav scroller (optional) **or** omit; primary navigation appears as bottom tabs or a top overflow menu.
  * Right: “Donate” button.

**Logo/Icon:**

* PurdueTHINK “P” monogram (light gray “I” stem + blue “P”).
* Size: **32×32px** icon box (kept vector).
* Placement: left, vertically centered.

**Text Elements (if showing inline nav):**

* Items: `Home`, `People`, `Apply`, `Projects`, `Client Interest`, `Consulting`
* Style: Poppins **Medium 14px**, **#FFFFFF** at 80% opacity (rgba(255,255,255,0.8))
* Active item: **#FFFFFF** 100% + 2px underline (pill underline length = intrinsic text width). Underline offset: 6px below baseline.

**Buttons:**

* **Donate** (primary CTA):

  * Text: “Donate”
  * Size: **Height 40px**, horizontal padding **16px**; min width **92px**
  * Radius: **16px**
  * Background: **#FFFFFF**
  * Text: **#000000**, Poppins **SemiBold 14px**
  * Press: background to **#17D4D4**, text **#000000**
  * Focus ring (accessibility): **#17D4D4** 2px outer glow for 180ms

**Effects:**

* Optional bottom divider hairline: **rgba(255,255,255,0.08)** at y=72

**Padding & Margins:**
Top safe inset respected; **padding-left/right: 24px**

**Responsiveness:**

* Header stays fixed; on scroll, opacity remains 1.
* If you implement a scroll-shrink, reduce to **60px** and scale logo to **28px**.

**Animation:**

* Donate button: ripple (Android) / scale to 0.98 on press (iOS) for **120ms**.

**Styling consistency:**

* All header nav items use the same typography and underline treatment for “active”.

**Component hierarchy:**

```json
{ "screen": "App Header",
  "components": [
    { "type": "logo", "id": "brandMark" },
    { "type": "nav", "items": ["Home", "People", "Apply", "Projects", "Client Interest", "Consulting"] },
    { "type": "button", "id": "donateCta", "variant": "primary" }
  ]
}
```

---

# Screen 1 — Home / Hero (“PurdueTHINK Consulting”)

**Background:** Solid black **#000000**

**Layout:**

* **Vertical stack, centered left** (not fully centered).
* Top spacing below header: **40px**.
* Content width: **342px** (390 − 24 − 24).
* Hero block height target: ~**300–360px** to allow breathable whitespace.

**Logo (optional light mark):**

* Keep header logo only; no large hero logo needed per screenshot.

**Text Elements:**

1. **Hero Title:**

   * Content: “**PurdueTHINK Consulting**”
   * Font: Poppins **Bold 36px** (line height 42px)
   * Color: **#FFFFFF**
   * Alignment: Left
   * Letter spacing: **−0.2px**
2. **Hero Subtitle:**

   * Content: “**Consulting for Purdue by Purdue.**”
   * Font: Poppins **Medium 18px** (line height 26px)
   * Color: rgba(255,255,255,0.88)
   * Margin-top from title: **12px**

**Buttons:** *(None on hero in screenshot)*

**Effects:**

* No gradient; pure solid background.

**Padding / Margins:**

* Horizontal padding: **24px**
* Bottom spacing to next section: **28px**

**Responsiveness:**

* Title scales down to **32px** at 320–360 widths; maintains 2-line wrap if needed.

**Animation/Transitions:**

* On load, **slide-fade up** (Y: 12px → 0px, opacity 0 → 1 over **280ms**); subtitle delayed by **60ms**.

**Styling consistency:**

* All hero typography is white on black; do not mix blues except for accents later.

**Component hierarchy:**

```json
{ "screen": "Home - Hero",
  "components": [
    { "type": "title", "text": "PurdueTHINK Consulting" },
    { "type": "subtitle", "text": "Consulting for Purdue by Purdue." }
  ]
}
```

---

# Screen 2 — Home / Who We Are (Image + Copy + “Join Us”)

**Background:** Solid black **#000000**

**Layout (two-column to single-column stack on mobile):**

* **Stack order on mobile:** Image → Text → Button
* Section top margin from hero: **24px**
* Section padding: **24px** horizontal; **20px** vertical

**Image Block (group photo):**

* Aspect ratio approx. **3:2**
* Render size on mobile: **342×228px**, radius **16px**
* Shadow: standard global shadow
* Margin-bottom: **16px**

**Text Elements:**

1. **Section Title:**

   * Content: “**Who We Are**”
   * Font: Poppins **SemiBold 22px** (lh 28px)
   * Color: **#FFFFFF**
   * Alignment: Left
   * Margin-bottom: **8px**
2. **Body Copy:**

   * Content (from screenshot):
     “**PurdueTHINK is a student-run consulting organization that is home to some of the most driven individuals at Purdue University.**”
   * Font: Poppins **Regular 16px** (lh 24px)
   * Color: rgba(255,255,255,0.84)
   * Max width: **342px**
   * Margin-bottom: **16px**

**Button:**

* Label: **“Join Us”**
* Size: **Height 48px**, min-width **140px**
* Radius: **16px**
* Background: **#17D4D4**
* Text: **#000000**, Poppins **SemiBold 16px**
* Hover/tap: darken background to **#12B9B9**; pressed scale 0.98 for **100ms**
* Focus ring: 2px **#17D4D4** glow for **160ms**

**Effects:**

* No gradients; use photo shadow only.

**Padding & Margins:**

* Between elements: 8–16px rhythm. Bottom to next section: **28px**

**Responsiveness:**

* On wide devices, you can switch to side-by-side (Image left 48%, Text + Button right 48%) with **24px** gutter.

**Animation:**

* Image **parallax fade** on scroll (10% translateY) optional; button slide-in.

**Styling consistency:**

* Buttons keep **16px radius** across the app.

**Component hierarchy:**

```json
{ "screen": "Home - Who We Are",
  "components": [
    { "type": "image", "id": "groupPhoto" },
    { "type": "title", "text": "Who We Are" },
    { "type": "paragraph", "text": "PurdueTHINK is a student-run consulting organization that is home to some of the most driven individuals at Purdue University." },
    { "type": "button", "id": "joinUsCta", "variant": "primary" }
  ]
}
```

---

# Screen 3 — Home / Mission & Values (Split)

**Background:** Solid black **#000000**

**Layout:**

* Section top padding: **24px**; bottom: **12px**
* **Stacked** on mobile: “Our Mission” card first, then “Our Values” accordion.
* Content width: **342px**

**Left Block — Our Mission:**

* **Title:** “**Our Mission**”

  * Poppins **SemiBold 24px**, **#FFFFFF**, margin-bottom **10px**
* **Body:**

  * “**We believe in creating a Purdue where students are embedded in the evolution of the university…**” (use full paragraph you need)
  * Poppins **Regular 16px**, lh **24px**, color rgba(255,255,255,0.86)
* **Spacing:** 16px between paragraphs; bottom margin **20px**

**Right Block — Our Values (Accordion):**

* **Title:** “**Our Values**”

  * Poppins **SemiBold 24px**, **#FFFFFF**, margin-bottom **12px**
* **Accordion Items** (each is a row with chevron/plus icon on right):

  * Items: **Adaptable**, **Collaborative**, **Impact Driven**
  * Row height: **56px**, full width **342px**
  * Text: Poppins **Medium 18px**, **#FFFFFF**
  * Divider below each row: **rgba(255,255,255,0.12)** 1px
  * Right icon: **+** or chevron, **24×24px**, color **#FFFFFF** at 80%
  * **Expanded panel:**

    * Body: Poppins **Regular 15px**, lh **22px**, color rgba(255,255,255,0.82); padding **12px 0 16px 0**

**Buttons:** *(None)*

**Effects:**

* Hairline divider between Mission & Values blocks is **optional** on mobile.

**Padding / Margins:**

* Section outer padding: **24px**
* Spacing between Mission and Values: **24px**

**Responsiveness:**

* On tablets/large, render **2-column**: Mission left (50%), Values right (50%) with **24px** gutter.

**Animation:**

* Accordion expand/collapse: height + opacity transition **220ms** cubic-bezier(0.2,0,0,1).

**Styling consistency:**

* All section titles use the same 24px/white style.

**Component hierarchy:**

```json
{ "screen": "Home - Mission & Values",
  "components": [
    { "type": "section", "id": "mission",
      "children": [
        { "type": "title", "text": "Our Mission" },
        { "type": "paragraph", "text": "We believe in creating a Purdue where students are embedded in the evolution of the university..." }
      ]
    },
    { "type": "section", "id": "values",
      "children": [
        { "type": "title", "text": "Our Values" },
        { "type": "accordion",
          "items": [
            { "title": "Adaptable" },
            { "title": "Collaborative" },
            { "title": "Impact Driven" }
          ]
        }
      ]
    }
  ]
}
```

---

# Screen 4 — Home / Learn More + Footer

**Background:** Solid black **#000000**

**Layout:**

* **Learn More**: Text left, supporting image right in desktop; on mobile stack as Text → Image → Button.
* Section padding: **24px**
* Use card-like spacing.

**Text Elements:**

1. **Body paragraph** (from screenshot’s lead-in about helping student orgs/departments):

   * Poppins **Regular 16px**, lh **24px**, color rgba(255,255,255,0.86)
   * Margin-bottom: **16px**
2. **Button:**

   * Label: **“Learn More”**
   * Height **48px**, radius **16px**
   * Background: **#FFFFFF**
   * Text: **#000000**, Poppins **SemiBold 16px**
   * Hover/tap: background **#17D4D4**, text **#000000**; pressed scale 0.98 for 100ms

**Image (speaker/classroom photo):**

* Render size: **342×220px**, radius **16px**, shadow as global
* Margin-top: **12px**

**Footer:**

* **Separator** above footer: 1px **rgba(255,255,255,0.12)**
* **Brand Title:** “**PurdueTHINK**”

  * Poppins **Bold 24px**, **#FFFFFF**, margin-bottom **16px**
* **Social Icons Row:** Instagram, Email, LinkedIn

  * Each **32×32px** circular tap area, icon color **#FFFFFF** 90%
  * Spacing **12px**
* **Link Columns** (stack on mobile):

  * Column 1: “**Our Team**”, “**Apply**”, “**Projects**”
  * Column 2: “**Consulting**”, “**Client Interest**”, “**Donate**”
  * Links: Poppins **Medium 16px**, **#FFFFFF** at 90%, line height **28px**
* **Copyright:** “© PurdueTHINK 2025”

  * Poppins **Regular 12px**, rgba(255,255,255,0.64), margin-top **16px**

**Padding & Margins:**

* Footer padding: **24px** top/bottom
* Spacing between footer groups: **18px**

**Responsiveness:**

* Links collapse into two stacked groups; social row remains single line and wraps if needed.

**Animations:**

* Icon buttons scale **0.96** on press.

**Component hierarchy:**

```json
{ "screen": "Home - Learn More + Footer",
  "components": [
    { "type": "paragraph", "text": "We help student organizations and departments at Purdue University accomplish their goals." },
    { "type": "button", "id": "learnMoreCta", "variant": "secondary" },
    { "type": "image", "id": "classroomPhoto" },
    { "type": "footer",
      "children": [
        { "type": "brand", "text": "PurdueTHINK" },
        { "type": "social", "items": ["instagram", "email", "linkedin"] },
        { "type": "links", "columns": [
          ["Our Team", "Apply", "Projects"],
          ["Consulting", "Client Interest", "Donate"]
        ]},
        { "type": "legal", "text": "© PurdueTHINK 2025" }
      ]
    }
  ]
}
```

---

# Screen 5 — People / Executive Board (Header + First Row)

**Background:** Solid black **#000000**

**Layout:**

* Top spacing below header: **28px**
* Content width: **342px**
* **Title first**, then a card grid of portraits (single column on narrow mobile, but you can show **3 cards vertically** with equal spacing).

**Text Elements:**

1. **Page Title:** “**2025 Executive Board**”

   * Poppins **Bold 32px** (lh 38px)
   * Color: **#FFFFFF**
   * Alignment: Center
   * Margin-bottom: **18px**

**Portrait Cards (first row of 3 in screenshot):**

* Each card:

  * **Image:** 1:1.1 ratio (slightly taller than square)

    * Size: **342×260px** (single column). If you choose a 3-across carousel, use **~104×164px** each with 12px gutters.
    * Radius: **16px**
    * Shadow: global
  * **Name Label:** under image

    * Poppins **SemiBold 18px**, **#FFFFFF**, centered
    * Margin-top: **10px**
* Example names (visible):

  * “Tessa Nappi”, “Aryan Bakshi”, “Shivani Sinha”

**Buttons:** *(None)*

**Effects:**

* Optional thin divider between rows: **rgba(255,255,255,0.08)**

**Padding & Margins:**

* Vertical spacing between cards: **20px**
* Between image and name: **10px**
* Section bottom padding: **12px**

**Responsiveness:**

* For tablets/wide: 2-column grid (card width **(100% − 24px) / 2** with 24px gutter).
* Maintain consistent image radius **16px**.

**Animation:**

* Lazy-fade images (opacity 0→1 over 240ms) as they enter viewport.

**Styling consistency:**

* All member name labels use the same font size/weight.

**Component hierarchy:**

```json
{ "screen": "People - Executive Board",
  "components": [
    { "type": "title", "text": "2025 Executive Board" },
    { "type": "list",
      "itemType": "personCard",
      "items": [
        { "imageId": "tessaNappiPhoto", "name": "Tessa Nappi" },
        { "imageId": "aryanBakshiPhoto", "name": "Aryan Bakshi" },
        { "imageId": "shivaniSinhaPhoto", "name": "Shivani Sinha" }
      ]
    }
  ]
}
```

---

# Screen 6 — People / Members Grid (Extended gallery)

**Background:** Solid black **#000000**

**Layout:**

* **Masonry-like** but keep it simple as a uniform **grid** on mobile.
* Grid: **1 column** on 390px; **2 columns** ≥428px; gutter **16px**.
* Content padding: **24px**

**Member Card:**

* **Image:**

  * Size: **(342px) × 256px** (single column) or **( (390 − 24 − 24 − 16)/2 ≈ 163px ) × 200px** (two-column)
  * Radius: **16px**
  * Shadow: global
* **Name:** Poppins **Medium 16px**, **#FFFFFF**, centered
* **Optional role line** (if you add roles later): Poppins **Regular 14px**, rgba(255,255,255,0.72), centered

**Buttons:**

* *(None)*; tap on a card can open a profile detail.

**Effects:**

* Card hover (web) / press: subtle lift translateY **−2px**, shadow stronger (0 10 24 rgba(0,0,0,0.26)).

**Padding / Margins:**

* Between rows: **18px**
* Between image and name: **8px**

**Responsiveness:**

* Auto-wrap grid by available width; keep gutters consistent.

**Animation:**

* Staggered fade-in per row (60ms delay per card).

**Styling consistency:**

* All cards share the same radius, spacing, and typography.

**Component hierarchy:**

```json
{ "screen": "People - Members Grid",
  "components": [
    { "type": "grid",
      "columns": { "default": 1, ">=428px": 2 },
      "itemType": "personCard",
      "items": [
        { "imageId": "member01", "name": "Member Name" },
        { "imageId": "member02", "name": "Member Name" }
        // ...repeat for all members
      ]
    }
  ]
}
```

---

# Screen 7 — Top-Level Navigation (Optional tab bar for mobile app)

*(Not shown on the website, but helpful for an app build mirroring the site IA.)*

**Background:** Solid black **#000000** with a top 1px divider **rgba(255,255,255,0.12)**

**Items:** `Home`, `People`, `Apply`, `Projects`, `More`

* Icon size **24×24px**; label Poppins **Medium 11px**
* Active color: **#17D4D4**; inactive: rgba(255,255,255,0.64)
* Safe-area aware (iPhone home indicator)

**Height:** **64px** + bottom safe inset

**Animation:**

* Active item cross-fade + scale **1.0 → 1.06** for **120ms**

**Component hierarchy:**

```json
{ "screen": "Bottom Tabs",
  "components": [
    { "type": "tabbar",
      "tabs": ["Home", "People", "Apply", "Projects", "More"]
    }
  ]
}
```

---

## Notes on Responsiveness & Accessibility

* **Typography scaling:** allow OS text scaling; clamp titles within 30–36px to avoid overflow.
* **Contrast:** All text on black meets AA with white/near-white.
* **Hit targets:** donate/join/learn buttons and social icons ≥44px.
* **Images:** use `contentMode: cover`, keep focal point center.
* **Performance:** lazy-load below-the-fold images; reuse header.

---

## Consistency Rules (apply app-wide)

* **Buttons:** radius **16px**, bold label, press scale **0.98**, focus ring **#17D4D4**.
* **Cards/Images:** radius **16px**, same shadow recipe.
* **Section paddings:** horizontal **24px**, vertical **20–28px**.
* **Section titles:** Poppins SemiBold **22–24px**, **#FFFFFF**.
* **Link look:** Underline on press; color stays **#FFFFFF** unless it’s the primary CTA (then use **#17D4D4** background).

---

If you want, I can also output this as a **single JSON design schema** or convert to **Tailwind tokens + React component structure** for your generator.
