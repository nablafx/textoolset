from flask import Flask, request, jsonify, render_template
from core.parsers import parse_tex, prune_bib, unify_bib, clean_project_images
import os
import sys

# Determine where static files live. When running from source we use the
# repo's `assets/` directory; when running from a PyInstaller onefile bundle
# the files are extracted to sys._MEIPASS and the assets will be located
# at <_MEIPASS>/assets (PyInstaller command used: --add-data "assets;assets").
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    static_folder_path = os.path.join(sys._MEIPASS, 'assets')
else:
    # Running from source
    static_folder_path = os.path.join(os.path.dirname(__file__), 'assets')

# Serve at URL path '/assets' so templates can use url_for('static', ...)
app = Flask(__name__, static_folder=static_folder_path, static_url_path='/assets')


@app.route('/')
def pruner_page():
    return render_template('bib_cleaner.html', active_page='bib_cleaner')


@app.route('/unifier')
def unifier_page():
    return render_template('bib_unifier.html', active_page='bib_unifier')


@app.route('/images')
def image_cleaner_page():
    return render_template('image_cleaner.html', active_page='image_cleaner')


@app.route('/api/prune', methods=['POST'])
def api_prune():
    bib_file = request.files['bib_file']
    tex_files = request.files.getlist('tex_files')
    bib_content = bib_file.read().decode('utf-8', errors='ignore')

    all_keys = set()
    for tf in tex_files:
        all_keys.update(parse_tex(tf.read().decode('utf-8', errors='ignore')))

    cleaned, log, stats, entries_map = prune_bib(bib_content, all_keys)

    # And make sure you include the entries_map in your JSON response:
    return jsonify({
        "result": cleaned,
        "log": log,
        "stats": stats,
        "total_used": stats["verified"],
        "entries_map": entries_map  # Add this line so the frontend can see the diffs
    })


@app.route('/api/unify', methods=['POST'])
def api_unify():
    bib_file = request.files['bib_file']
    target = request.form.get('target', 'bibtex')  # Get target from radio/select
    bib_content = bib_file.read().decode('utf-8', errors='ignore')

    unified, log, stats = unify_bib(bib_content, target)
    return jsonify({"result": unified, "log": log, "stats": stats, "target": target})


@app.route('/api/clean_images', methods=['POST'])
def api_clean_images():
    project_path = request.form.get('project_path', '').strip()
    tex_files = request.files.getlist('tex_files')
    
    tex_texts = []
    for tf in tex_files:
        tex_texts.append(tf.read().decode('utf-8', errors='ignore'))
        
    deleted, kept = clean_project_images(project_path, tex_texts)
    
    return jsonify({
        "deleted": deleted,
        "kept": kept,
        "stats": {
            "deleted_count": len(deleted),
            "kept_count": len(kept)
        }
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)