import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

def generate_html(csv_file, template_dir='templates', template_file='template.html', output_file='index.html'):
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{csv_file}' is empty.")
        return
    except Exception as e:
        print(f"An error occurred while reading '{csv_file}': {e}")
        return

    # Convert DataFrame to list of dictionaries
    jobs = df.to_dict(orient='records')

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(searchpath=template_dir))
    try:
        template = env.get_template(template_file)
    except Exception as e:
        print(f"Error loading template: {e}")
        return

    # Render the template with job data
    html_content = template.render(jobs=jobs)

    # Write the rendered HTML to a file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file '{output_file}' has been generated successfully.")

def main():
    csv_file = 'web3_career_jobs.csv'
    generate_html(csv_file)

if __name__ == "__main__":
    main()
