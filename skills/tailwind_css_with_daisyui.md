# Tailwind CSS with DaisyUI Integration

## Overview
This micro-skill document provides a comprehensive guide to integrating Tailwind CSS with the DaisyUI component library for rapid and streamlined UI development. It covers configuration, design system setup, component library creation, responsive design implementation, and dark mode toggle functionality.

---

## 1. Tailwind CSS and DaisyUI Configuration

### Purpose
Configure the `tailwind.config.js` file to integrate DaisyUI, define foundational settings, and extend the design system with DaisyUI's components and utilities.

### Key Code Snippets and Patterns
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: '#1f2937',
        ink: '#111827',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
      },
      spacing: {
        '1/2': '0.125rem',
        '3/4': '0.1875rem',
      },
      borderRadius: {
        '3xl': '1.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
};
```

### Common Errors and Prevention
- **Error**: DaisyUI plugin not installed or not included in the `plugins` array.
  - **Solution**: Ensure DaisyUI is installed via npm (`npm install daisyui`) and included in the `plugins` array in `tailwind.config.js`.
- **Error**: Incorrect color naming or conflicts with DaisyUI's default colors.
  - **Solution**: Use clear and unique naming conventions for custom colors to avoid conflicts with DaisyUI's predefined color schemes.

---

## 2. Tailwind Play CDN with DaisyUI Integration

### Purpose
Integrate Tailwind CSS and DaisyUI into a single HTML page without using build tools by leveraging the Tailwind Play CDN.

### Key Code Snippets and Patterns
```html
<!-- Include Tailwind CSS and DaisyUI via Play CDN -->
<script src="https://cdn.tailwindcss.com?plugins=forms,typography,daisyui"></script>

<!-- Custom Tailwind Configuration -->
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          brand: '#1f2937',
          ink: '#111827',
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
        },
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
          serif: ['Merriweather', 'serif'],
        },
        spacing: {
          '1/2': '0.125rem',
          '3/4': '0.1875rem',
        },
        borderRadius: {
          '3xl': '1.5rem',
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('daisyui'),
    ],
  };
</script>

<!-- Custom Base and Components -->
<style type="text/tailwindcss">
  @layer base {
    /* Custom base styles */
    h1 {
      @apply text-2xl font-bold;
    }
  }
  @layer components {
    /* Custom components using DaisyUI */
    .btn {
      @apply btn btn-primary;
    }
    .card {
      @apply card bg-base-100 shadow-xl;
    }
  }
  @layer utilities {
    /* Custom utilities */
    .filter-none {
      filter: none;
    }
  }
</style>
```

### Common Errors and Prevention
- **Error**: DaisyUI plugin not included in the Play CDN URL.
  - **Solution**: Ensure the `plugins` parameter in the CDN URL includes `daisyui`.
- **Error**: Incorrect `tailwind.config` setup, leading to custom colors or DaisyUI components not working.
  - **Solution**: Verify that the `tailwind.config` is correctly configured and that DaisyUI is properly integrated.

---

## 3. Component Library Design with DaisyUI

### Purpose
Design and implement a component library using DaisyUI's pre-built components, ensuring a consistent and responsive design language.

### Key Code Snippets and Patterns
```html
<!-- Button Components -->
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>

<!-- Card Components -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content goes here.</p>
    <div class="card-actions">
      <button class="btn btn-primary">Action 1</button>
      <button class="btn btn-secondary">Action 2</button>
    </div>
  </div>
</div>

<!-- Form Components -->
<input type="text" class="input input-bordered" placeholder="Enter text">
```

### Common Errors and Prevention
- **Error**: Inconsistent or incorrect class naming for DaisyUI components.
  - **Solution**: Use DaisyUI's predefined class names and ensure consistency across the project.
- **Error**: DaisyUI components not rendering as expected.
  - **Solution**: Verify that DaisyUI is properly installed and included in the `tailwind.config.js` and that the correct classes are used.

---

## 4. Responsive Design Implementation with DaisyUI

### Purpose
Implement responsive design using Tailwind CSS and DaisyUI to ensure the webpage displays well on various devices and screen sizes.

### Key Code Snippets and Patterns
```html
<div class="container mx-auto">
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Grid items -->
  </div>
</div>
```

### Common Errors and Prevention
- **Error**: Incorrect breakpoint setup, causing layout issues on certain screen sizes.
  - **Solution**: Use Tailwind's provided breakpoint classes like `sm:`, `md:`, `lg:`, `xl:`, `2xl:` and consider design requirements for different devices.
- **Error**: DaisyUI components not responsive.
  - **Solution**: Ensure that DaisyUI components are used with Tailwind's responsive classes and that the layout is designed to be responsive.

---

## 5. Dark Mode Toggle with DaisyUI

### Purpose
Implement a dark mode toggle feature using DaisyUI, allowing users to switch between light and dark themes.

### Key Code Snippets and Patterns
```html
<!-- Theme Initialization (system + localStorage + no flash) -->
<script>
  (function initTheme() {
    const isDarkMode = localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    }
    // Additional initialization code...
  })();
</script>

<!-- Toggle Button -->
<button class="btn btn-ghost" onclick="toggleTheme()">Toggle Theme</button>

<script>
  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }
</script>
```

### Common Errors and Prevention
- **Error**: Dark mode toggle not applying correctly.
  - **Solution**: Ensure the `dark` class is added to the `<html>` tag and that DaisyUI's dark mode styles are properly configured.
- **Error**: Flash of unstyled content during theme switch.
  - **Solution**: Apply dark mode immediately on page load and use `localStorage` to save the user's choice to prevent flashing.

---

## Conclusion
By following this guide, you can effectively integrate Tailwind CSS with the DaisyUI component library, ensuring a robust, responsive, and user-friendly design system. Always remember to test your configurations and components across different devices and screen sizes to maintain consistency and usability.