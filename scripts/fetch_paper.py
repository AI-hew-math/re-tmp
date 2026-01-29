#!/usr/bin/env python3
"""
Fetch paper metadata and content from arxiv.

Usage:
    python scripts/fetch_paper.py 1706.03762              # arxiv ID
    python scripts/fetch_paper.py https://arxiv.org/abs/1706.03762
    python scripts/fetch_paper.py 1706.03762 --key transformer  # custom key
    python scripts/fetch_paper.py 1706.03762 --full       # include full tex

Outputs YAML for papers.yaml and creates papers/<key>.md template.
"""
import argparse
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from textwrap import dedent
import tarfile
import io


def extract_arxiv_id(input_str: str) -> str:
    """Extract arxiv ID from URL or raw ID."""
    # Handle URLs like https://arxiv.org/abs/1706.03762 or arxiv.org/pdf/1706.03762.pdf
    match = re.search(r'(\d{4}\.\d{4,5})(v\d+)?', input_str)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract arxiv ID from: {input_str}")


def fetch_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from arxiv API."""
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    with urllib.request.urlopen(url, timeout=10) as response:
        xml_data = response.read()
    
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    entry = root.find('atom:entry', ns)
    if entry is None:
        raise ValueError(f"Paper not found: {arxiv_id}")
    
    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
    
    authors = []
    for author in entry.findall('atom:author', ns):
        name = author.find('atom:name', ns).text
        authors.append(name)
    
    # Format authors: "Last1, Last2, and Last3" or "Last1 et al."
    if len(authors) > 3:
        author_str = authors[0].split()[-1] + " et al."
    else:
        last_names = [a.split()[-1] for a in authors]
        if len(last_names) == 1:
            author_str = last_names[0]
        elif len(last_names) == 2:
            author_str = f"{last_names[0]} and {last_names[1]}"
        else:
            author_str = f"{', '.join(last_names[:-1])}, and {last_names[-1]}"
    
    summary = entry.find('atom:summary', ns).text.strip()
    published = entry.find('atom:published', ns).text[:4]  # Year
    
    # Try to find primary category for venue hint
    categories = [c.get('term') for c in entry.findall('atom:category', ns)]
    
    return {
        'title': title,
        'authors': author_str,
        'authors_full': authors,
        'year': published,
        'arxiv': arxiv_id,
        'abstract': summary,
        'categories': categories,
    }


def fetch_source(arxiv_id: str) -> str | None:
    """Try to fetch tex source from arxiv."""
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        
        # Try to extract from tar.gz
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.tex'):
                        f = tar.extractfile(member)
                        if f:
                            return f.read().decode('utf-8', errors='ignore')
        except tarfile.TarError:
            # Might be plain tex
            try:
                return data.decode('utf-8', errors='ignore')
            except:
                pass
    except Exception as e:
        print(f"Could not fetch source: {e}")
    
    return None


def generate_key(title: str) -> str:
    """Generate a short key from title."""
    # Take first significant word(s)
    words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
    stopwords = {'a', 'an', 'the', 'of', 'for', 'and', 'in', 'on', 'to', 'with', 'is', 'are'}
    key_words = [w for w in words if w not in stopwords][:2]
    return '-'.join(key_words) if key_words else 'paper'


def main():
    parser = argparse.ArgumentParser(description="Fetch arxiv paper metadata and content")
    parser.add_argument("arxiv", help="arxiv ID or URL")
    parser.add_argument("--key", "-k", help="Custom key for papers.yaml")
    parser.add_argument("--full", "-f", action="store_true", help="Fetch full tex source")
    parser.add_argument("--create", "-c", action="store_true", help="Create papers/<key>.md file")
    args = parser.parse_args()
    
    arxiv_id = extract_arxiv_id(args.arxiv)
    print(f"Fetching {arxiv_id}...")
    
    meta = fetch_metadata(arxiv_id)
    key = args.key or generate_key(meta['title'])
    
    # Print YAML for papers.yaml
    print("\n" + "=" * 60)
    print("Add to literature/papers.yaml:")
    print("=" * 60)
    print(f"""
{key}:
  title: "{meta['title']}"
  authors: "{meta['authors']}"
  year: {meta['year']}
  venue: "arXiv"  # Update after publication
  arxiv: "{meta['arxiv']}"
  repo: ""  # TODO: Find official repo
  tags: []
  notes: ""
  details: papers/{key}.md
""")
    
    # Print abstract
    print("=" * 60)
    print("Abstract:")
    print("=" * 60)
    print(meta['abstract'])
    
    # Fetch source if requested
    source = None
    if args.full:
        print("\nFetching source...")
        source = fetch_source(arxiv_id)
        if source:
            print(f"✓ Got {len(source)} chars of tex source")
        else:
            print("✗ Could not fetch source (may need manual download)")
    
    # Create notes file if requested
    if args.create:
        template_path = Path("literature/papers/.template.md")
        output_path = Path(f"literature/papers/{key}.md")
        
        if output_path.exists():
            print(f"\n⚠️  {output_path} already exists, skipping")
        else:
            template = template_path.read_text() if template_path.exists() else ""
            
            # Fill in template
            content = template
            content = content.replace("{Paper Title}", meta['title'])
            content = content.replace("{key}", key)
            content = content.replace("{authors}", meta['authors'])
            content = content.replace("{year}", meta['year'])
            content = content.replace("{venue}", "arXiv")
            content = content.replace("{arxiv_url}", f"https://arxiv.org/abs/{meta['arxiv']}")
            content = content.replace("{repo_url}", "TODO")
            
            # Add source if available
            if source:
                content = content.replace("[PASTE FULL PAPER TEXT / TEX HERE]", source[:50000])  # Limit size
            
            output_path.write_text(content)
            print(f"\n✓ Created {output_path}")


if __name__ == "__main__":
    main()
