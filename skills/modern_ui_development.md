# Modern UI Development with Tailwind CSS and DaisyUI

## Overview
This micro-skill focuses on developing modern, responsive, and accessible UI components using Tailwind CSS and DaisyUI. It covers the complete integration of Tailwind CSS with DaisyUI, setting up a scalable component library, adding interactive features, enhancing accessibility, and persisting user-selected themes.

## 1. Tailwind CSS and DaisyUI Integration

### Description
Integrate Tailwind CSS and DaisyUI to leverage the utility-first approach of Tailwind alongside DaisyUI's pre-designed components. This setup ensures a seamless development experience with a focus on customization and rapid prototyping.

### Key Code Snippets and Patterns
```html
<!-- Include Tailwind CSS via CDN -->
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/typography@0.5/dist/typography.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/forms@0.5/dist/forms.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/aspect-ratio@0.5/dist/aspect-ratio.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/daisyui@5/dist/full.css"></script>
<script src="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.js"></script>
```
```css
/* Define global theme variables */
:root {
  --primary: #4f46e5;
  --secondary: #9333ea;
  --background: #f9fafb;
  --text: #111827;
}
```

### Common Errors and Prevention
- **Error**: Missing or incorrect CDN links, causing Tailwind or DaisyUI styles to not load.
  - **Solution**: Double-check CDN URLs and ensure a stable internet connection.
- **Error**: Theme variables are not defined or improperly referenced, leading to inconsistent styling.
  - **Solution**: Define all theme variables within the `:root` selector and use them consistently across components.

## 2. Building Responsive and Interactive Components

### Description
Develop responsive and interactive UI components such as navigation bars, modals, and form elements. This involves using Tailwind's utility classes and DaisyUI's component classes to create adaptable and user-friendly interfaces.

### Key Code Snippets and Patterns
```html
<!-- Example of a responsive navigation bar -->
<nav class="bg-white shadow-md">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex">
        <a href="#" class="inline-flex items-center px-4 py-2 text-lg font-medium text-gray-800">Brand</a>
      </div>
      <div class="flex items-center">
        <button class="btn btn-primary">Sign Up</button>
      </div>
    </div>
  </div>
</nav>
```
```javascript
// Example of a modal toggle function
function toggleModal() {
  const modal = document.getElementById('modal');
  modal.classList.toggle('hidden');
}
```

### Common Errors and Prevention
- **Error**: Incorrect usage of utility classes, leading to layout issues.
  - **Solution**: Refer to Tailwind CSS documentation for correct class usage and ensure responsive design principles are followed.
- **Error**: Event handlers are not properly attached, causing interactive components to malfunction.
  - **Solution**: Verify that event handlers are correctly defined and attached to the appropriate elements.

## 3. Enhancing Accessibility

### Description
Implement accessibility features such as ARIA labels, keyboard navigation, and color contrast adjustments to make UI components usable for all users, including those with disabilities.

### Key Code Snippets and Patterns
```html
<!-- Example of a button with ARIA label and keyboard accessibility -->
<button class="btn btn-secondary" aria-label="Submit" accesskey="s">Submit</button>

<!-- Example of a modal with ARIA attributes -->
<div id="modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center" aria-modal="true" role="dialog">
  <div class="bg-white p-6 rounded-md">
    <p>Modal content</p>
    <button class="btn btn-primary mt-4" onclick="toggleModal()">Close</button>
  </div>
</div>
```

### Common Errors and Prevention
- **Error**: Missing or incorrect ARIA attributes, hindering accessibility.
  - **Solution**: Use appropriate ARIA attributes and validate accessibility using tools like Lighthouse or Axe.
- **Error**: Insufficient color contrast, affecting readability.
  - **Solution**: Use color contrast checkers to ensure compliance with WCAG standards.

## 4. Persisting User Preferences with Local Storage

### Description
Persist user-selected themes (light or dark) using the browser's localStorage to enhance user experience by maintaining preferences across sessions.

### Key Code Snippets and Patterns
```javascript
// Function to set the theme and persist it
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

// Function to apply the persisted theme on page load
function applyPersistedTheme() {
  const theme = localStorage.getItem('theme') || 'light';
  setTheme(theme);
}

// Apply the persisted theme when the page loads
window.addEventListener('DOMContentLoaded', applyPersistedTheme);
```

### Common Errors and Prevention
- **Error**: LocalStorage operations fail due to browser restrictions or insufficient permissions.
  - **Solution**: Implement fallback mechanisms or notify users if localStorage is unavailable.
- **Error**: Theme settings are not applied consistently, causing flickering or inconsistent UI.
  - **Solution**: Ensure that the theme is applied before the page renders by using the `DOMContentLoaded` event.

## Conclusion
By mastering these aspects of Tailwind CSS and DaisyUI-based UI development, you can create modern, responsive, and accessible web applications that provide a seamless user experience. This micro-skill equips you with the knowledge to set up a robust component library, implement interactive features, enhance accessibility, and persist user preferences effectively.