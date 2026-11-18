"""Server-render Arabic sharing metadata; social crawlers need no JavaScript."""
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- Social sharing metadata -->'
END = '<!-- /Social sharing metadata -->'


def metadata_for(relative):
    config = json.loads((ROOT / 'sharing.json').read_text(encoding='utf-8'))
    course = config['courses'].get(relative.parts[0], {})
    title = course.get('title', config['title'])
    description = course.get('description', config['description'])
    if relative.name == 'report.html':
        title = 'تقرير: ' + title
    elif relative.name.startswith('source-register-'):
        title = 'المصادر والمراجع | ' + config['site_name']
    elif relative.name.startswith('README-'):
        title = 'دليل الدراسة والمراجعة | ' + config['site_name']
    base = (os.environ.get('SITE_URL') or config.get('public_url', '')).strip().rstrip('/')
    if base and (urlsplit(base).scheme not in {'https', 'http'} or not urlsplit(base).netloc
                 or urlsplit(base).query or urlsplit(base).fragment):
        raise ValueError('SITE_URL must be an absolute HTTP(S) site URL without query or fragment')
    url = ''
    if base:
        path = relative.as_posix()
        if path.endswith('index.html'):
            path = path[:-len('index.html')]
        url = base + '/' + quote(path, safe='/')
    return config, title, description, url


def apply_metadata(document, relative):
    config, title, description, url = metadata_for(relative)
    document = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', document, flags=re.S)
    values = [('name', 'description', description),
              ('property', 'og:site_name', config['site_name']),
              ('property', 'og:title', title),
              ('property', 'og:description', description),
              ('property', 'og:type', 'article' if relative.name == 'report.html' else 'website'),
              ('property', 'og:locale', 'ar_MA'),
              ('name', 'twitter:card', 'summary'),
              ('name', 'twitter:title', title),
              ('name', 'twitter:description', description),
              ('name', 'theme-color', '#a82735')]
    if url:
        values.append(('property', 'og:url', url))
    tags = [f'<meta {kind}="{key}" content="{html.escape(value, quote=True)}">' for kind, key, value in values]
    if url:
        tags.append(f'<link rel="canonical" href="{html.escape(url, quote=True)}">')
    block = START + '\n' + '\n'.join(tags) + '\n' + END
    if '</head>' not in document:
        raise ValueError(f'No HTML head in {relative}')
    return document.replace('</head>', block + '\n</head>', 1)


if __name__ == '__main__':
    count = 0
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT)
        if any(part in {'_site', '.git', 'sources', 'assignment'} for part in relative.parts):
            continue
        path.write_text(apply_metadata(path.read_text(encoding='utf-8'), relative), encoding='utf-8')
        count += 1
    print(f'Updated Arabic social metadata in {count} source pages.')
