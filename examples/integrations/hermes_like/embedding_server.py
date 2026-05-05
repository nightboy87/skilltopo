from __future__ import annotations

from flask import Flask, jsonify, request

from skilltopo.semantic_match import DEFAULT_SEMANTIC_MODEL, SemanticMatcher

app = Flask(__name__)
matcher = SemanticMatcher(DEFAULT_SEMANTIC_MODEL)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok" if matcher.load() else "unavailable",
        "model_name": matcher.model_name,
        "model_loaded": matcher.available,
        "error": matcher.error,
    })


@app.post("/embed")
def embed():
    payload = request.get_json(force=True) or {}
    texts = payload.get("texts")
    if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
        return jsonify({"error": "Expected JSON body with string list field: texts"}), 400
    if not matcher.load():
        return jsonify({"error": matcher.error or "semantic model unavailable"}), 503
    return jsonify({"embeddings": [matcher.embed(text) for text in texts]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
