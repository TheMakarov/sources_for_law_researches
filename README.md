# Moroccan Law Study Workspace | مساحة دراسة القانون

A bilingual Arabic–English study site, with one selected topic for each of five courses. Includes seven-session study plans, concise reports, outlines, source references, research notes, and glossaries.

The visual theme uses Moroccan red, green, ivory, and geometric accents. All site paths are relative, so the site works under a GitHub Pages project URL.

## Local preview

```bash
python -m pip install -r requirements.txt
python scripts/build_pages.py
python -m http.server 8000 --directory _site
```

Open http://localhost:8000 in your browser. The build checks local page links, fragments, and assets.

## Publish on GitHub Pages

1. Create an empty GitHub repository. Do not add a README or other initial files there.
2. From this repository folder, connect it and push:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

3. In the GitHub repository, open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Open **Actions → Deploy study workspace to GitHub Pages → Run workflow**, or push another commit after enabling Pages.
5. The deployment job shows the published URL, normally `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`.

The workflow validates pull requests and deploys pushes to `main`. No custom domain, API key, or repository-specific base path is required.

See [GitHub’s workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Content layout

```text
01-introduction-to-law/  # Mandatory and default rules
02-legal-sociology/     # Social control through law
03-islamic-law/         # Custom and habit
04-political-science/   # Political authority
05-constitutional-law/  # Unitary and federal states
assets/                 # Shared Moroccan theme
scripts/build_pages.py  # Validated static-site build
.github/workflows/      # GitHub Pages deployment
```

Each course has `ar/` and `en/`. Edit the six Markdown study files in either language; the build updates the matching web sections and report page automatically. The root guides and source registers are also rendered from Markdown. Change `assets/theme.css` to adjust the colors and layout.

## Sources and assignment images

Downloaded `sources/` folders and personal `assignment/` photographs stay on your computer and are ignored by Git. The Pages build replaces offline source links with their recorded publisher URLs, so it works from a clean Git clone with no downloaded PDFs. These third-party sources retain their own rights and attribution. The source manifest records the editions and download provenance.

The reports are concise educational treatments, not official legal translations. Legal examples use the dated editions identified in the materials. Check relevant subsequent amendments and your instructor’s requirements before submission.

## Social link descriptions

Arabic titles and descriptions for WhatsApp, Telegram, and other link previews are configured in `sharing.json`. Every page includes static description, Open Graph, and Twitter Card tags; course and report links use their own Arabic titles and descriptions, including links to English pages.

GitHub Actions supplies the deployed base URL automatically, including a project repository subpath. For another host, set `public_url` in `sharing.json`, or build with `SITE_URL=https://your-domain.example/project python scripts/build_pages.py`. This adds absolute canonical and `og:url` URLs. Without a known public URL, local previews retain the descriptions and omit those URL tags rather than invent an address. Share the deployed public link; local file links cannot be fetched by messaging services. Existing preview caches may retain earlier descriptions.

## بالعربية

مساحة دراسة بخمس مواد، لكل منها نسخة عربية وأخرى إنجليزية. لتفعيل النشر: أنشئ مستودعا فارغا على GitHub، اربطه بالأوامر أعلاه، ثم اختر **GitHub Actions** من إعدادات **Pages**. تنشر الخطة تلقائيا عند الدفع إلى الفرع `main`.

تبقى ملفات المصادر الأصلية وصور الموضوعات محلية، وتفتح مراجع نسخة الويب على مواقع ناشريها. لتعديل الألوان، حرر `assets/theme.css`.
