"""Build deterministic synthetic evaluation PDFs; never call an AI provider."""
import hashlib
import json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import simpleSplit

ROOT = Path(__file__).resolve().parents[1]


def build():
    folder = ROOT / 'evaluation/heldout'
    corpus = json.loads((folder / 'corpus.json').read_text())
    output = ROOT / 'data/heldout_pdfs'
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for document in corpus['documents']:
        path = output / document['filename']
        canvas = Canvas(str(path), pagesize=(595, 842), invariant=1)
        canvas.setTitle(document['title'])
        for number, paragraphs in enumerate(document['pages'], 1):
            canvas.setFont('Helvetica-Bold', 18)
            canvas.drawString(48, 780, document['title'])
            canvas.setFont('Helvetica', 10)
            canvas.drawString(48, 758, 'Synthetic evaluation document | candidate-1')
            y = 700
            canvas.setFont('Helvetica', 12)
            for paragraph in paragraphs:
                for line in simpleSplit(paragraph, 'Helvetica', 12, 490):
                    canvas.drawString(48, y, line)
                    y -= 18
                y -= 20
            canvas.setFont('Helvetica', 10)
            canvas.drawString(48, 40, f'Physical PDF page {number}')
            canvas.showPage()
        canvas.save()
        hashes[document['filename']] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {'version':corpus['version'], 'status':'candidate; reviewer approval pending',
                'pdf_sha256':hashes}
    for name in ('corpus.json', 'questions.json'):
        manifest[name + '_sha256'] = hashlib.sha256((folder/name).read_bytes()).hexdigest()
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Built {len(hashes)} synthetic evaluation PDFs. Ground-truth review and live evaluation remain pending.')


if __name__ == '__main__':
    build()
