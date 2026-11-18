"""Build a GitHub Pages edition without uploading offline reference downloads."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import html
import json
import re
import shutil
import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
SKIP = {'.git', '.github', '_site', 'sources', 'assignment', 'scripts', '__pycache__', '.venv'}
ROOT_FILES = {'index.html', '.nojekyll', 'README-ar.md', 'README-en.md', 'source-register-ar.md', 'source-register-en.md'}
manifest = json.loads((ROOT / 'source-download-manifest.json').read_text(encoding='utf-8'))
source_urls = {(ROOT / row['folder'] / row['file']).resolve(): row['url'] for row in manifest}


def publisher_link(origin, target):
    if urlsplit(target).scheme or target.startswith('#'):
        return target
    path = unquote(target.split('#', 1)[0])
    return source_urls.get((origin.parent / path).resolve(), target)


def published_copy(text, origin):
    if origin.suffix == '.html':
        def link(match):
            value = html.unescape(match.group(2))
            return match.group(1) + html.escape(publisher_link(origin, value), quote=True) + match.group(3)
        text = re.sub(r'((?:href|src)=")([^"]*)(")', link, text)
        if origin.name == 'index.html' and origin.parent == ROOT:
            for stem in ['README-ar', 'README-en', 'source-register-ar', 'source-register-en']:
                text = text.replace(stem + '.md', stem + '.html')
            text = re.sub(r'<strong>\d+/\d+ source files saved locally\.</strong>',
                          '<strong>Read the sources through their publisher links.</strong>', text)
    else:
        text = re.sub(r'(\]\()([^\s]+)(\))',
                      lambda m: m.group(1) + publisher_link(origin, m.group(2)) + m.group(3), text)
    return text.replace('Open saved copy', 'Read source online').replace('فتح النسخة المحفوظة', 'قراءة المصدر على موقع ناشره')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.ids.update([values['id']] if 'id' in values else [])
        for key in ['href', 'src']:
            if key in values:
                self.targets.append(values[key])


def validate():
    errors = []
    documents = {}
    for path in OUT.rglob('*.html'):
        doc = Links()
        doc.feed(path.read_text(encoding='utf-8'))
        documents[path.resolve()] = doc
    for path, doc in documents.items():
        for target in doc.targets:
            if urlsplit(target).scheme:
                continue
            name, _, anchor = target.partition('#')
            if name.startswith('/'):
                errors.append(f'{path.relative_to(OUT)}: absolute URL breaks project Pages: {target}')
                continue
            resolved = (path.parent / unquote(name)).resolve() if name else path
            if not resolved.exists():
                errors.append(f'{path.relative_to(OUT)}: missing {target}')
            elif anchor and resolved in documents and unquote(anchor) not in documents[resolved].ids:
                errors.append(f'{path.relative_to(OUT)}: missing fragment {target}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Validated {len(documents)} HTML pages and all local links/assets.')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    # Snapshot the inputs first: never recurse into the generated output directory.
    paths = [p for p in ROOT.rglob('*') if p.is_file() and not any(part in SKIP for part in p.relative_to(ROOT).parts)]
    for path in paths:
        relative = path.relative_to(ROOT)
        if len(relative.parts) == 1 and path.name not in ROOT_FILES:
            continue
        if path.suffix not in {'.html', '.md', '.css', '.svg'} and path.name != '.nojekyll':
            continue
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = path.read_text(encoding='utf-8')
        target.write_text(published_copy(text, path), encoding='utf-8')

    # Markdown is the source of truth for all six study documents in each language.
    for course in sorted(ROOT.glob('0*')):
        for lang in ['ar', 'en']:
            source_folder = course / lang
            output_folder = OUT / course.name / lang
            index_path = output_folder / 'index.html'
            index = index_path.read_text(encoding='utf-8')
            for number, filename in enumerate(['01-study-plan.md', '02-report-outline.md', '03-report.md', '04-sources.md', '05-research-notes.md', '06-glossary.md'], 1):
                source = source_folder / filename
                content = published_copy(source.read_text(encoding='utf-8'), source)
                if number == 3:
                    report_path = output_folder / 'report.html'
                    report = report_path.read_text(encoding='utf-8')
                    report = re.sub(r'(<main><section>).*?(</section></main>)',
                                    lambda m: m.group(1) + markdown.markdown(content, extensions=['tables']) + m.group(2),
                                    report, flags=re.S)
                    report_path.write_text(report, encoding='utf-8')
                    continue
                edit_label = 'الملف القابل للتحرير' if lang == 'ar' else 'Editable file'
                rendered = markdown.markdown(content, extensions=['tables'])
                section = f'<section id="s{number}">{rendered}<p class="noprint"><a href="{filename}">{edit_label}</a></p></section>'
                index = re.sub(rf'<section id="s{number}">.*?</section>', lambda m: section, index, flags=re.S)
            index_path.write_text(index, encoding='utf-8')

    # Present the source registers and reading guides as proper web pages.
    for name in ['README-ar', 'README-en', 'source-register-ar', 'source-register-en']:
        lang = 'ar' if name.endswith('-ar') else 'en'
        direction = 'rtl' if lang == 'ar' else 'ltr'
        content = (OUT / (name + '.md')).read_text(encoding='utf-8')
        notice = ('نسخة الويب: تفتح المراجع على مواقع ناشريها. تتوفر التنزيلات الأصلية في حزمة الدراسة المحلية.' if lang == 'ar'
                  else 'Web edition: references open on their publishers’ websites. Original downloads remain in your local study bundle.')
        rendered = markdown.markdown(content, extensions=['tables'])
        title = 'دليل الدراسة والمصادر' if lang == 'ar' else 'Study guide and sources'
        page = f'''<!doctype html><html lang="{lang}" dir="{direction}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="assets/theme.css"></head><body><header><h1>{title}</h1><nav><a href="index.html">Home / الرئيسية</a></nav></header><main><section><p>{notice}</p>{rendered}</section></main></body></html>'''
        (OUT / (name + '.html')).write_text(page, encoding='utf-8')
    validate()
    print('GitHub Pages output:', OUT)
    print('Reference PDFs and assignment photographs are excluded from publication.')


if __name__ == '__main__':
    main()
