#!/bin/bash

# Script to update all HTML files in pildoras directory with dark theme
# Excludes pildoras.html as requested

echo "Updating HTML files in pildoras directory with dark theme..."

# Dark theme CSS to apply
DARK_CSS="<style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 2em;
            color: #e0e0e0;
            background-color: #121212;
        }
        h1, h2 {
            color: #ffffff;
        }
        h1 {
            border-bottom: 2px solid #bb86fc;
            padding-bottom: 0.5em;
        }
        h2 {
            margin-top: 1.5em;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #1e1e1e;
            padding: 2em;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        code, pre {
            background-color: #2d2d2d;
            padding: 2px 6px;
            border: 1px solid #444;
            border-radius: 4px;
            color: #f44336;
            font-family: \"Courier New\", Courier, monospace;
        }
        pre {
            padding: 1em;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .card {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 6px;
            margin-bottom: 1.5em;
            padding: 1.5em;
        }
        .card-body {
            color: #e0e0e0;
        }
        footer {
            color: #b0b0b0;
            border-top: 1px solid #444;
        }
        a {
            color: #bb86fc;
            text-decoration: none;
        }
        a:hover {
            color: #9d4edd;
        }
        strong {
            color: #ffffff;
        }
        ul {
            list-style-type: disc;
            padding-left: 20px;
        }
    </style>"

# Find all HTML files except pildoras.html
files=$(find pildoras -name "*.html" -not -name "pildoras.html")

for file in $files; do
    echo "Processing $file..."

    # Check if file already has dark theme (contains #121212 background)
    if grep -q "background-color: #121212" "$file"; then
        echo "  Already has dark theme, skipping..."
        continue
    fi

    # Create backup
    cp "$file" "${file}.backup"

    # Replace the entire style block
    sed -i '/<style>/,/<\/style>/c\'"$DARK_CSS" "$file"

    echo "  Updated $file"
done

echo "All files have been updated with dark theme!"
echo "Backup files created with .backup extension"
