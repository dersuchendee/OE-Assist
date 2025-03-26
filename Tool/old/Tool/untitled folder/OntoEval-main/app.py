from flask import Flask, render_template, request, redirect, url_for, session
import csv
import datetime
import os
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Application startup")

# Ensure responses.csv exists with the proper header
if not os.path.exists('responses.csv'):
    with open('responses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user', 'cqid', 'modelled_or_not', 'difficulty'])
    logging.info("Created responses.csv with header")

# Load CSV data into a global list
data = []
with open('data.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)
logging.info(f"Loaded {len(data)} rows from data.csv")


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Initial page: User enters their own ID and selects the ordering.
    The ID and ordering are saved along with the current date/time.
    """
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        ordering = request.form.get('ordering')  # Either "A_first" or "B_first"
        session['user_id'] = user_id
        session['ordering'] = ordering
        session['start_time'] = datetime.datetime.now().isoformat()
        session['responses'] = []  # initialize list to store question responses
        logging.info(f"User '{user_id}' logged in at {session['start_time']} with ordering '{ordering}'")
        return redirect(url_for('intro'))
    return render_template('index.html')


@app.route('/intro', methods=['GET', 'POST'])
def intro():
    """
    Introduction page: Display an example text.
    """
    if request.method == 'POST':
        user_id = session.get('user_id', 'anonymous')
        logging.info(f"User '{user_id}' moved from intro to questions")
        # Start questions from the first row
        return redirect(url_for('question', q_index=0))
    return render_template('intro.html')


@app.route('/question/<int:q_index>', methods=['GET', 'POST'])
def question(q_index):
    """
    Main question page:
    - Displays the CQ (and, if applicable, the LLM suggestion).
    - Presents the answer selection and difficulty rating.
    - The questions are shown in the order determined by the user's selection.
    """
    user_id = session.get('user_id', 'anonymous')
    ordering = session.get('ordering', 'A_first')

    # Create a sorted version of data based on the ordering.
    # If ordering is "A_first", all rows with setting "A" come first.
    # If ordering is "B_first", all rows with setting "B" come first.
    if ordering == "A_first":
        sorted_data = sorted(data, key=lambda row: 0 if row['setting'] == 'A' else 1)
    else:  # "B_first"
        sorted_data = sorted(data, key=lambda row: 0 if row['setting'] == 'B' else 1)

    if q_index >= len(sorted_data):
        logging.info(f"User '{user_id}' completed all questions")
        return redirect(url_for('finished'))

    current_row = sorted_data[q_index]
    # For display, show the LLM suggestion only if the question's setting is B.
    show_llm = (current_row['setting'] == 'B')

    if request.method == 'POST':
        # Retrieve the clicked response. It will be "Yes", "No", or "I don't know"
        user_response = {
            'cqid': current_row['cqid'],
            'is_modeled': request.form.get('is_modeled'),
            'difficulty': request.form.get('difficulty')
        }
        # Store response in session if needed
        responses = session.get('responses', [])
        responses.append(user_response)
        session['responses'] = responses

        # Write the response to responses.csv
        with open('responses.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([user_id, current_row['cqid'], user_response['is_modeled'], user_response['difficulty']])
        logging.info(
            f"User '{user_id}' answered question {current_row['cqid']} with '{user_response['is_modeled']}' and difficulty {user_response['difficulty']}")

        # Continue to next question or to questionnaire page.
        # (For example, here you could also implement a checkpoint every N questions if needed.)
        next_index = q_index + 1
        # If you want to add checkpoints (e.g., every 5 responses), adjust the condition accordingly.
        return redirect(url_for('question', q_index=next_index))

    return render_template('question.html', q_index=q_index, current_row=current_row, show_llm=show_llm)


@app.route('/questionnaire/<int:step>', methods=['GET', 'POST'])
def questionnaire(step):
    """
    Intermediate page(s) after a certain number of questions.
    Displays a link to a questionnaire and some example text.
    """
    user_id = session.get('user_id', 'anonymous')
    if request.method == 'POST':
        logging.info(f"User '{user_id}' completed questionnaire at step {step}")
        if step < len(data):
            return redirect(url_for('question', q_index=step))
        else:
            return redirect(url_for('finished'))
    return render_template('questionnaire.html', step=step)


@app.route('/finished')
def finished():
    """
    Finished page: Display a final message.
    """
    user_id = session.get('user_id', 'anonymous')
    logging.info(f"User '{user_id}' has finished the questionnaire")
    return render_template('finished.html')


if __name__ == '__main__':
    app.run(debug=True)
