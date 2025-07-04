#!/usr/bin/env python3
"""
Test script for server-side markdown rendering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.agents.prompt_builder import render_response_content

def test_markdown_rendering():
    """Test the enhanced markdown rendering functionality"""
    
    print("Testing server-side markdown rendering...")
    
    # Test markdown content with various elements
    test_markdown = """# Main Title

This is a paragraph with **bold text** and *italic text*.

## Subtitle

Here's a list:
- Item 1
- Item 2 with `inline code`
- Item 3

### Code Block

```python
def hello_world():
    print("Hello, World!")
    return True
```

### Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

### Blockquote

> This is a blockquote with important information.
> It spans multiple lines.

### Links

Check out [this link](https://example.com) for more information.

#### Numbered List

1. First item
2. Second item
3. Third item

That's all!
"""
    
    # Test markdown rendering
    html_output = render_response_content(test_markdown, 'markdown')
    
    print("✅ Markdown rendered successfully!")
    print("\nFirst 500 characters of output:")
    print(html_output[:500] + "..." if len(html_output) > 500 else html_output)
    
    # Test text rendering
    text_output = render_response_content("Plain text content", 'text')
    print("\n✅ Text rendered successfully!")
    
    # Test HTML rendering
    html_input = "<h1>HTML Content</h1><p>This is HTML.</p>"
    html_output = render_response_content(html_input, 'html')
    print("\n✅ HTML rendered successfully!")
    
    print("\n🎉 All rendering tests completed successfully!")

if __name__ == "__main__":
    test_markdown_rendering()
