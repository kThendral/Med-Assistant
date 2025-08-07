from flask import Flask, render_template, request
from gemini_helper import query_gemini
from retriever import index_documents, get_similar_doc

app = Flask(__name__)
index_documents()

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    if request.method == "POST":
        symptoms = request.form["symptoms"]
        doc_info = get_similar_doc(symptoms)
        prompt = f"The patient shows these symptoms: {symptoms}. Based on the following medical info:\n{doc_info}\nSuggest a diagnosis and a sample prescription."
        result = query_gemini(prompt)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
