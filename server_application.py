from flask import Flask, jsonify, request, abort
from survey_DAO import survey_DAO

app = Flask(__name__, static_url_path = '', static_folder = 'HTML')


@app.route('/')
def index():
    return "Server is running - go to http://127.0.0.1:5000/survey.html to begin"


#curl "http://127.0.0.1:5000/survey"
@app.route('/survey')
def getAll():
    #print("in getall")
    results = survey_DAO.getAll()
    return jsonify(results)


#curl "http://127.0.0.1:5000/survey/2"
@app.route('/survey/<int:id>')
def findByResponseID(id):
    foundRecord = survey_DAO.findByResponseID(id)

    return jsonify(foundRecord)


#curl  -i -H "Content-Type:application/json" -X POST http://127.0.0.1:5000/survey -d "{\"EmployeeID\":16,\"IT_Overall_Score\":6,\"Laptop_Score\":4,\"Accessories_Score\":5,\"Applications_Score\":3, \"Support_Score\":7, \"Positive_Feedback\":\"IT support agents are very helpful\", \"Negative_Feedback\":\"Theres too much bloatware on our laptops. Mine can barely function with only a handful of apps open. Our accessories e.g. headsets should be wireless by default. Also, SFDC is a pain, theres always an outage\", \"Follow_Up\":\"No\"}"
#curl  -i -H "Content-Type:application/json" -X POST http://127.0.0.1:5000/survey -d "{\"EmployeeID\":1,\"IT_Overall_Score\":10,\"Laptop_Score\":10,\"Accessories_Score\":10,\"Applications_Score\":9, \"Support_Score\":10, \"Positive_Feedback\":\"Everything is great\", \"Negative_Feedback\":\"Nothing to report!\", \"Follow_Up\":\"Yes\"}" 
@app.route('/survey', methods=['POST'])
def create():
    
    if not request.json:
        abort(400)
        
    survey_response = {
        "EmployeeID": request.json['EmployeeID'],
        "IT_Overall_Score": request.json['IT_Overall_Score'],
        "Laptop_Score": request.json['Laptop_Score'],
        "Accessories_Score": request.json['Accessories_Score'],
        "Applications_Score": request.json['Applications_Score'],
        "Support_Score": request.json['Support_Score'],
        "Positive_Feedback": request.json['Positive_Feedback'],
        "Negative_Feedback": request.json['Negative_Feedback'],
        "Follow_Up": request.json['Follow_Up']
    }
    values = (survey_response['EmployeeID'],survey_response['IT_Overall_Score'],survey_response['Laptop_Score'],
        survey_response['Accessories_Score'],survey_response['Applications_Score'],survey_response['Support_Score'],
        survey_response['Positive_Feedback'],survey_response['Negative_Feedback'],survey_response['Follow_Up'])
    newId = survey_DAO.create(values)
    survey_response['ResponseID'] = newId
    return jsonify(survey_response)


#curl  -i -H "Content-Type:application/json" -X PUT http://127.0.0.1:5000/survey/6 -d "{\"Applications_Score\":10, \"Follow_Up\":\"No\"}"
@app.route('/survey/<int:id>', methods=['PUT'])
def update(id):
    foundRecord = survey_DAO.findByResponseID(id)
    if not foundRecord:
        abort(404)
    
    if not request.json:
        abort(401)
    reqJson = request.json
    
    if 'EmployeeID' in reqJson:
        foundRecord['EmployeeID'] = reqJson['EmployeeID']
    if 'IT_Overall_Score' in reqJson:
        foundRecord['IT_Overall_Score'] = reqJson['IT_Overall_Score']
    if 'Laptop_Score' in reqJson:
        foundRecord['Laptop_Score'] = reqJson['Laptop_Score']
    if 'Accessories_Score' in reqJson:
        foundRecord['Accessories_Score'] = reqJson['Accessories_Score']
    if 'Applications_Score' in reqJson:
        foundRecord['Applications_Score'] = reqJson['Applications_Score']
    if 'Support_Score' in reqJson:
        foundRecord['Support_Score'] = reqJson['Support_Score']
    if 'Positive_Feedback' in reqJson:
        foundRecord['Positive_Feedback'] = reqJson['Positive_Feedback']
    if 'Negative_Feedback' in reqJson:
        foundRecord['Negative_Feedback'] = reqJson['Negative_Feedback']
    if 'Follow_Up' in reqJson:
        foundRecord['Follow_Up'] = reqJson['Follow_Up']

    values = (foundRecord['EmployeeID'],foundRecord['IT_Overall_Score'],foundRecord['Laptop_Score'],
        foundRecord['Accessories_Score'],foundRecord['Applications_Score'],foundRecord['Support_Score'],foundRecord['Positive_Feedback'],
            foundRecord['Negative_Feedback'],foundRecord['Follow_Up'],foundRecord['ResponseID'])


    survey_DAO.update(values)
    return jsonify(foundRecord)
        

# curl -X DELETE http://127.0.0.1:5000/survey/6
@app.route('/survey/<int:id>' , methods=['DELETE'])
def delete(id):
    survey_DAO.delete(id)
    return jsonify({"done":True})


#curl "http://127.0.0.1:5000/survey/stats"
@app.route('/survey/stats')
def getStats():
    results = survey_DAO.get_survey_stats()
    return jsonify(results)


if __name__ == '__main__' :
    app.run(debug= True)
    print("Working")