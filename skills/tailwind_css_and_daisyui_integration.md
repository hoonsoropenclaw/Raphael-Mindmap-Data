# Tailwind CSS and DaisyUI Integration

## Overview
This micro-skill document provides a comprehensive guide to integrating Tailwind CSS with the DaisyUI component library to accelerate UI development. It covers configuration, design system setup, component customization, responsive design, and dark mode functionality.

---

## 1. Tailwind CSS and DaisyUI Integration

### Purpose
Integrate Tailwind CSS with DaisyUI to leverage pre-designed components while maintaining Tailwind's utility-first approach for customization.

### Key Code Snippets and Patterns
```html
<!-- Include Tailwind CSS and DaisyUI via CDN -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>

<!-- Configure Tailwind to work with DaisyUI -->
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          primary: '#1f2937',
          secondary: '#111827',
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
    plugins: [require('daisyui')],
  };
</script>
```

### Common Errors and Prevention
- **Error**: DaisyUI styles not applying correctly.
  - **Solution**: Ensure the DaisyUI CSS is included before Tailwind CSS and that the `plugins` array in `tailwind.config.js` includes `daisyui`.
- **Error**: Conflicting class names between Tailwind and DaisyUI.
  - **Solution**: Use clear and consistent naming conventions and prioritize DaisyUI classes for component-level styles.

---

## 2. Component Customization with DaisyUI

### Purpose
Customize DaisyUI components using Tailwind utility classes to match your design requirements.

### Key Code Snippets and Patterns
```html
<!-- Customized Button -->
<button class="btn btn-primary text-white bg-blue-500 hover:bg-blue-600">Primary Button</button>

<!-- Customized Card -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content goes here.</p>
    <div class="card-actions justify-end">
      <button class="btn btn-secondary">Action</button>
    </div>
  </div>
</div>
```

### Common Errors and Prevention
- **Error**: Overriding DaisyUI styles unintentionally.
  - **Solution**: Use Tailwind utility classes judiciously and understand the specificity of DaisyUI classes.
- **Error**: Inconsistent component styling across the project.
  - **Solution**: Define a set of custom utility classes or components in your `tailwind.config.js` to maintain consistency.

---

## 3. Responsive Design with Tailwind and DaisyUI

### Purpose
Implement responsive design using Tailwind's responsive utilities in conjunction with DaisyUI components.

### Key Code Snippets and Patterns
```html
<!-- Responsive Grid Layout -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Grid items -->
</div>

<!-- Responsive Navbar -->
<nav class="navbar bg-base-100">
  <div class="navbar-start">
    <span class="text-lg">Navbar</span>
  </div>
  <div class="navbar-center lg:hidden">
    <button class="btn btn-square btn-ghost">
      <!-- Hamburger icon -->
    </button>
  </div>
  <div class="navbar-end">
    <a class="btn btn-ghost btn-sm" href="#">Home</a>
    <a class="btn btn-ghost btn-sm" href="#">About</a>
    <a class="btn btn-ghost btn-sm" href="#">Contact</a>
  </div>
</nav>
```

### Common Errors and Prevention
- **Error**: Incorrect breakpoint usage leading to layout issues.
  - **Solution**: Use Tailwind's responsive classes consistently and test layouts across different devices.
- **Error**: DaisyUI components not behaving responsively.
  - **Solution**: Ensure that DaisyUI components are used with appropriate Tailwind responsive classes and that the component library is up-to-date.

---

## 4. Dark Mode Implementation

### Purpose
Implement a dark mode toggle feature using Tailwind's dark mode functionality and DaisyUI's dark mode support.

### Key Code Snippets and Patterns
```html
<!-- Theme Initialization -->
<script>
  (function initTheme() {
    const isDarkMode = localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    }
  })();
</script>

<!-- Toggle Button -->
<button class="btn btn-ghost" onclick="toggleTheme()">
  <!-- Theme icon -->
</button>

<script>
  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }
</script>
```

### Common Errors and Prevention
- **Error**: Dark mode not applying correctly.
  - **Solution**: Ensure the `dark` class is added to the `<html>` tag and that DaisyUI's dark mode styles are properly configured.
- **Error**: Flash of unstyled content during theme switch.
  - **Solution**: Apply dark mode immediately on page load and use `localStorage` to save the user's choice.

---

## 5. Best Practices and Tips

### Purpose
Provide best practices and tips for effective integration of Tailwind CSS and DaisyUI.

### Key Code Snippets and Patterns
- **Consistent Naming Conventions**: Use clear and consistent naming conventions for classes and components to maintain readability and maintainability.
- **Modular Components**: Break down components into smaller, reusable parts to enhance reusability and scalability.
- **Customization with Tailwind**: Leverage Tailwind's utility classes for customization rather than overriding DaisyUI styles directly.
- **Testing Across Devices**: Regularly test your UI across different devices and screen sizes to ensure responsiveness and consistency.

### Common Errors and Prevention
- **Error**: Overcomplicating component structure.
  - **Solution**: Keep component structures simple and modular, and avoid unnecessary nesting.
- **Error**: Inconsistent styling due to lack of planning.
  - **Solution**: Plan your design system and component library in advance, and use tools like Figma or Sketch to prototype and visualize components.

---

## Conclusion
By following this guide, you can effectively integrate Tailwind CSS with DaisyUI, creating a powerful and flexible UI development environment. This combination allows for rapid development of responsive and visually appealing interfaces while maintaining the flexibility and customization capabilities of Tailwind CSS.