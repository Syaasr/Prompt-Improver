# Design System: Prompt Refiner (Python Edition)
**Project ID:** Prompt-Improver-Py

## 1. Visual Theme & Atmosphere
**"Engineered Clarity (Python Native)"**

Adhering to the "Intentional Minimalism" philosophy, this Pure Python implementation maximizes `streamlit` capabilities while enforcing strict aesthetic discipline via strict CSS injection. The goal is to make a Streamlit app that *doesn't look like* a default Streamlit app.

**Key Aesthetic Principles:**
*   **Solid & Flat:** No default Streamlit gradients.
*   **Tactile Feedback:** Custom CSS transitions on buttons and inputs.
*   **Orange Accent:** (#F97316) serves as the singular "Call to Action" and focus indicator.

## 2. Color Palette

*   **Backgrounds:**
    *   Dark: `#0F172A` (Slate 900)
    *   Light: `#F8FAFC` (Slate 50) - *Controlled via Streamlit Theme config if possible, else CSS override.*
*   **Accent (The Signal):**
    *   **Orange:** `#F97316` (Orange 500)
*   **Surface:**
    *   Sidebar: `#1E293B` (Slate 800)

## 3. Typography
**Font:** Roboto (Google Fonts)
*   Forced via CSS injection: `font-family: 'Roboto', sans-serif !important;`

## 4. Component Stylings (CSS Targets)

*   **Buttons (`st.button`):**
    *   `border-radius: 0.5rem !important;`
    *   `background-color: #F97316 !important;` (Primary action)
    *   `color: white !important;`
    *   `transition: all 0.3s ease-in-out !important;`
    *   *Hover:* darken background, scale 1.02.

*   **Inputs (`st.text_area`, `st.text_input`):**
    *   `border: 1px solid #CBD5E1;`
    *   `border-radius: 0.5rem;`
    *   *Focus:* `border-color: #F97316; box-shadow: 0 0 0 1px #F97316;`

*   **Navigation (`sac.menu`):**
    *   Use `streamlit-antd-components` default dark theme but override accent color to Orange.

## 5. Layout Principles
*   **Sidebar:** Collapsible icon-only mode is the default preference for "Avant-Garde" minimalism.
*   **Main Stage:** Centered max-width container to prevent line-length exhaustion on large screens.
