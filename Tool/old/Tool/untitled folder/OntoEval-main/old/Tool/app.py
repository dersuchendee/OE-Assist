from flask import Flask, request, jsonify, render_template
import os
import uuid
import json
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key='key')

# Folder to store feedback JSON files
FEEDBACK_FOLDER = 'feedback'
os.makedirs(FEEDBACK_FOLDER, exist_ok=True)

# New: Folder to store ontology and CQ inputs
STORAGE_FOLDER = 'storage'
os.makedirs(STORAGE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-llm', methods=['POST'])
def process_llm():
    data = request.get_json()
    ontology = data.get('ontology', '')
    competency_question = data.get('competency_question', '')

    storage_record = {
        "id": uuid.uuid4().hex,
        "ontology": ontology,
        "competency_question": competency_question
    }
    storage_filename = os.path.join(STORAGE_FOLDER, f"input_{storage_record['id']}.json")
    try:
        with open(storage_filename, 'w') as f:
            json.dump(storage_record, f, indent=2)
    except Exception as e:
        # Log or handle the error accordingly; here we just print
        print("Error saving input:", e)

    prompt = (
        f'''
Here is an ontology and a competency question with its story. you need to do CQ-verification to check if the competency question is supported by the ontology or not. If yes, write yes and write an
SPARQL query for us. If no, write a short description for Why this CQ is not supported.


examples:


@prefix : <http://www.example.org/test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .


:Cl_Person a owl:Class .
:Cl_Band a owl:Class .
:Cl_Membership a owl:Class .


:memberOf a owl:ObjectProperty ;
    rdfs:domain :Cl_Membership ;
    rdfs:range :Cl_Band .


:member a owl:ObjectProperty ;
    rdfs:domain :Cl_Membership ;
    rdfs:range :Cl_Person .


:startDate a owl:DatatypeProperty ;
    rdfs:domain :Cl_Membership ;
    rdfs:range xsd:date .


:endDate a owl:DatatypeProperty ;
    rdfs:domain :Cl_Membership ;
    rdfs:range xsd:date .


CQ:  What are the members of a certain band at a certain point in time?
Answer: Yes.
Here the CQ is answerable since the CQ is a Reification CQ (means all classes and datatypes in CQ are connected to a reified class in the ontology (Cl_Membership)). Else it is not answerable.


CQ: What band this person is member of?
answer: Yes.
Because through a reification we can connect person and band even if this CQ can be answered by a simple connection from Person to Band


CQ: Name of this person?
answer: No
There is no data property


Location of this person?
answer: No
There is no object property from Person to a class or property Location or "NewYork"




"Ontology:\n{ontology}\n\n"
        "Competency Question:\n{competency_question}\n\n"
'''
    )

    messages = [
        {"role": "system", "content": "You are an ontology engineer expert."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0
        )
        llm_output = response.choices[0].message.content.strip()
        return jsonify({'llm_output': llm_output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save-feedback', methods=['POST'])
def save_feedback():
    data = request.get_json()
    llm_output = data.get('llm_output', '')
    comments = data.get('comments', '')
    feedback_status = data.get('feedback_status', '')

    record = {
        "id": uuid.uuid4().hex,
        "llm_output": llm_output,
        "comments": comments,
        "feedback_status": feedback_status
    }
    filename = os.path.join(FEEDBACK_FOLDER, f"feedback_{record['id']}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(record, f, indent=2)
        return jsonify({'message': 'Feedback saved successfully!', 'record_id': record['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
