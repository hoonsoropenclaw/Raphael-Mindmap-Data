# UI Development with Visual Hierarchy

## Overview
This micro-skill focuses on developing and validating user interfaces using the Tailwind CSS framework, creating dynamic visual hierarchies and micro-animations, and integrating a Node Inspector for debugging and displaying detailed node information. It covers extending Tailwind CSS configurations, applying utility classes, creating custom animations, ensuring HTML tag balance and structural completeness, and implementing a responsive Node Inspector.

---

## 1. Tailwind CSS Configuration Extension

### Purpose
Extend Tailwind CSS's default settings to incorporate custom colors, fonts, and shadows, enabling a more personalized and visually appealing design system.

### Key Techniques
- **Custom Colors**: Define unique color palettes to match brand identity or specific design requirements.
- **Custom Fonts**: Incorporate web fonts to enhance typography and improve readability.
- **Custom Shadows**: Create distinct shadow styles to add depth and emphasis to UI elements.

### Code Example
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        ink: { /* Define ink color properties */ },
        brand: { /* Define brand color properties */ },
        mint: '#5cf2c0',
        rose: '#ff6f9c',
        amber: '#ffc857',
        violet: '#9b7bff'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        soft: '0 8px 30px -8px rgba(0,0,0,.45)',
        glow: '0 0 0 1px rgba(122,169,255,.35), 0 0 24px rgba(79,125,255,.45)'
      }
    }
  },
  // ... other configurations
};
```

### Common Errors and Prevention
- **Undefined Custom Properties**: Forgetting to place custom properties within the `extend` block causes Tailwind to ignore them.
  - **Solution**: Always nest custom properties within the `extend` block.
- **Incorrect Color Formats**: Using invalid hexadecimal codes or missing the `#` symbol.
  - **Solution**: Validate color formats and ensure hexadecimal codes are correctly specified.

---

## 2. Utility Class Application

### Purpose
Utilize Tailwind CSS utility classes to rapidly apply styles to HTML elements, such as animations, shadows, and button designs, ensuring a consistent and responsive design across different devices.

### Key Techniques
- **Predefined Classes**: Leverage Tailwind's extensive library of utility classes for quick and efficient styling.
- **Responsive Design**: Implement responsive classes to ensure compatibility and adaptability across various devices and screen sizes.
- **State Variants**: Apply styles based on user interactions, such as hover, focus, and active states, to enhance user experience.

### Code Example
```html
<!-- Button with primary style and fade-in animation -->
<button class="btn-primary anim-fade">Click Me</button>

<!-- Card with lift-up effect on hover and enlarged shadow -->
<div class="card-lift hover:shadow-lg">
  <!-- Card content -->
</div>

<!-- Skeleton loading element -->
<div class="skeleton"></div>
```

### Common Errors and Prevention
- **Misspelled Class Names**: Incorrectly spelled class names prevent styles from applying.
  - **Solution**: Double-check class names against the Tailwind CSS documentation.
- **Improper Class Order**: Incorrect order of classes can lead to unintended style overrides.
  - **Solution**: Understand Tailwind's style precedence and adjust class order as needed.

---

## 3. Custom CSS Keyframes Creation

### Purpose
Create custom CSS animations using `@keyframes` to add dynamic effects like fading, popping, and shimmering, enhancing the visual appeal and interactivity of web pages.

### Key Techniques
- **Animation Definitions**: Define animations with clear start and end states to ensure smooth and predictable transitions.
- **Timing Functions**: Use `cubic-bezier` for smoother and more natural transitions, providing a more polished look.
- **Animation Properties**: Apply animations to elements using `animation` properties, specifying duration, timing, and iteration counts.

### Code Example
```css
/* Define custom keyframes animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  0% { transform: scale(0); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

/* Apply animations to elements */
.btn-primary {
  animation: fadeIn 0.5s ease-in-out;
}

.card-lift {
  animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.skeleton {
  animation: shimmer 2s linear infinite;
}
```

### Common Errors and Prevention
- **Uneven Animation Transitions**: Transitions between keyframes may appear abrupt or unnatural.
  - **Solution**: Utilize `cubic-bezier` to fine-tune the timing function for smoother animations.
- **Mismatched Animation Names**: Discrepancies between animation names in CSS and HTML lead to animations not triggering.
  - **Solution**: Ensure consistent naming of animations across CSS and HTML files.

---

## 4. HTML Validation Tools

### Overview
The **html_validation_tools** component ensures the correctness and integrity of HTML documents by validating tag balance and structural completeness, preventing rendering issues and maintaining web page quality.

### 1. HTML Tag Balance Validator

#### Description
This tool verifies that every HTML tag opened has a corresponding closing tag, maintaining proper document structure and preventing rendering issues.

#### Key Code Snippet
```python
from html.parser import HTMLParser

class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void = {"br","hr","img","input","meta","link","source","area","base","col","embed","param","track","wbr"}

    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"close {tag} with empty stack @ {self.getpos()}")
            return
        if self.stack[-1][0] != tag:
            self.errors.append(f"close {tag} but top is {self.stack[-1][0]} @ {self.getpos()}, opened @ {self.stack[-1][1]}")
        self.stack.pop()

# Usage Example
b = Balance()
with open("index.html", encoding="utf-8") as file:
    html_content = file.read()
b.feed(html_content)
if b.errors:
    print("Tag Balance Errors:", b.errors)
```

#### Common Errors and Prevention
1. **Unclosed Tags**: Ensure every opening tag has a corresponding closing tag or is self-closing.
   - **Prevention**: Use HTML validators to automatically detect unclosed tags.
2. **Incorrect Tag Nesting**: Verify that tags are properly nested to maintain the correct hierarchy.
   - **Prevention**: Follow a consistent nesting order and use indentation to visualize the structure.
3. **Misinterpretation of Void Elements**: Void elements (e.g., `<br />`, `<img />`) should be correctly identified to avoid false positives.
   - **Prevention**: Maintain a whitelist of void elements within the validator.

### 2. HTML Structure Validator

#### Description
This tool checks for the presence of essential HTML tags and ensures that the overall document structure is complete and correctly formatted.

#### Key Code Snippet
```python
import re
from collections import Counter

def validate_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Check for required tags
    required_tags = ['<!DOCTYPE html>', '<html>', '</html>', '<head>', '</head>', '<body>', '</body>']
    for tag in required_tags:
        if tag not in html:
            return False
    # Check tag balance
    opens = re.findall(r'<(?!!|/)([a-z][a-z0-9]*)\b', html)
    closes = re.findall(r'</([a-z][a-z0-9]*)>', html)
    oc = Counter(opens)
    cc = Counter(closes)
    for tag in oc:
        if tag not in cc or oc[tag] != cc[tag]:
            return False
    return True
```

#### Common Errors and Prevention
1. **Missing Essential Tags**: Ensure that all required tags (e.g., `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`) are present.
   - **Prevention**: Use templates or boilerplate code to include essential tags by default.
2. **Unbalanced Tags**: Use regular expressions to verify that every opening tag has a corresponding closing tag.
   - **Prevention**: Implement automated checks to catch unbalanced tags early in the development process.
3. **Handling Void Tags**: Exclude void elements from balance checks to prevent incorrect error reporting.
   - **Prevention**: Maintain a list of void tags and adjust the validation logic accordingly.

### 3. Best Practices and Recommendations

#### Error Prevention
- **Consistent Indentation**: Proper indentation improves readability and makes it easier to spot structural issues.
- **Automated Validation**: Integrate HTML validators into your development workflow to catch errors during coding.
- **Regular Code Reviews**: Conduct peer reviews to identify and rectify structural issues collaboratively.

#### Extending the Tool
- **Detailed Reporting**: Enhance the tool to provide more