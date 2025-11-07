# MakeSkilled Bootcamp Website

Stack: Flask (Python) + HTML/Tailwind + MongoDB Atlas

## Quickstart

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set MongoDB configuration (optional — defaults provided):

```bash
$env:MONGODB_URI="mongodb+srv://shaikabdul:1234@build.yiikjuc.mongodb.net/?retryWrites=true&w=majority&appName=Build"
$env:MONGODB_DB="makeskilled_bootcamp"
$env:MONGODB_COLLECTION="colleges"
```

3. Run the app:

```bash
python app.py
```

Open http://localhost:5000

## Proposal Download
Place your file at:
`static/docs/Gen-AI-Bootcamp-brochure.docx`

The hero button downloads this file. If you prefer a remote PDF link, update `static/js/main.js` accordingly.

## WhatsApp Link
Configured to `+91 7893015625`. Update in `templates/index.html` if needed.

## Data Persistence
- Primary: MongoDB Atlas (`colleges` collection)
- Backup log: `data/registrations.json`

## Project Structure
```
bootcampms/
  app.py
  requirements.txt
  templates/
    index.html
  static/
    css/custom.css
    js/main.js
    images/ (place logos)
    docs/ Gen-AI-Bootcamp-brochure.docx (optional)
  data/ registrations.json
```

## Notes
- Tailwind is loaded via CDN for simplicity.
- This project avoids React; animations use Tailwind transitions and lightweight JS.


# genai-bootcamp
# bootcamp-website
