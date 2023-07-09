from flask import Flask, request, redirect, render_template, flash, jsonify, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, surveys

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)



@app.route('/')
def show_homepage():
    
    return render_template('home.html', survey_list=surveys)

@app.route("/session-init", methods=['POST'])
def initiate_session():
    surveyTitle = request.form['survey-title']
    survey_id = surveys[surveyTitle].title

    if (request.cookies.get(f"completed_{survey_id}") == "yes"):
        flash("You've already completed that survey. Please try another survey.")
        return redirect('/')
    else:
        session['survey'] = surveyTitle
        session['responses']=[]
        
        return redirect('/question/0')


@app.route('/question/<int:qid>')
def show_question(qid):
    """display proper question and choices"""

    survey = surveys[session['survey']]

    if (session['responses'] is None):
        #arrived at question page too soon
        flash("You're a little ahead of the game. Let's try again.")
        return redirect('/')
    
    if (len(session['responses']) == len(survey.questions)):
        #they've completed the survey
        return redirect('/end')
    
    if (len(session['responses']) != qid):
        #accessing questions out of order
        flash("Oops. You accidentally got off course. Let's help.")
        return redirect(f'/question/{len(session["responses"])}')
    
    
    question = survey.questions[qid]
    return render_template('question.html', qid=qid, question=question)

    
@app.route('/answer', methods=["POST"])
def post_answer():
    """collect answer and route user to next question or end if all questions have been answered."""
    # maintain correct survey from session
    survey = surveys[session['survey']]
    
    
    # add response value to session['responses']
    response = {"answer": request.form['answer'], 'text':request.form.get('text_response', '')}
    responses = session['responses']
    responses.append(response)
    session['responses'] = responses

    # route to next step
    if (len(session['responses']) == len(survey.questions)):
        return redirect('/end')
    else:
        return redirect(f'/question/{len(session["responses"])}')
    
@app.route('/end')
def show_thank_you():
    """survey is finished. Show the thank you page"""

    responses = session['responses']
    survey = surveys[session['survey']]
    survey_id = survey.title
    content = make_response(render_template('end.html', 
                                            survey=survey,
                                            responses=responses))    
    content.set_cookie(f"completed_{survey_id}", "yes")
    return content