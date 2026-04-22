from flask import Flask, request, jsonify, render_template
from core.parsers import parse_tex, prune_bib, unify_bib

app = Flask(__name__)


@app.route('/')
def pruner_page():
    return render_template('bib_cleaner.html', active_page='bib_cleaner')


@app.route('/unifier')
def unifier_page():
    return render_template('bib_unifier.html', active_page='bib_unifier')


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


if __name__ == '__main__':
    app.run(debug=True, port=5000)