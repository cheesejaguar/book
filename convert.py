import re

# Path to your markdown file
input_file = 'book.txt'
output_file = 'output.txt'

# Read the markdown file
with open(input_file, 'r', encoding='utf-8') as file:
    content = file.read()

# Regular expression to match markdown chapter headers
pattern = r'### Chapter (\d+): (.+)'

# Replacement pattern for LaTeX syntax
replacement = r'\\chapter{\2}'

# Perform the replacement
latex_content = re.sub(pattern, replacement, content)

# Write the updated content to a new file
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(latex_content)

print(f"Conversion complete. LaTeX content saved to {output_file}.")