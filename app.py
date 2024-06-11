from flask import Flask, request, jsonify
import uuid
import re
from math import ceil
from datetime import datetime

app = Flask(__name__)

receipts = {}

def calcPoints(receipt):
    points = 0

    #rule 1 One point for every alphanumeric character in the retailer name.
    points += sum(char.isalnum() for char in receipt['retailer'])

    #50 points if the total is a round dollar amount with no cents.
    total = float(receipt['total'])
    if total.is_integer():
        points += 50
    
    #25 points if the total is a multiple of 0.25.
    if (total % .25 == 0):
        points += 25
    
    #5 points for every two items on the receipt.
    if len(receipt['items']) % 2 == 0:
        points += (len(receipt['items']) / 2) *5
    
    #If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
    for item in receipt['items']:
        if len(item['shortDescription'].strip()) % 3 ==0:
            points += ceil(float(item['price']) * 0.2)
    
   # 6 points if the day in the purchase date is odd.
    purchase_date = datetime.strptime(receipt['purchaseDate'], "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6
    
    #10 points if the time of purchase is after 2:00pm and before 4:00pm.
    purchaseTime = datetime.strptime(receipt['purchaseTime']," %H:%M")
    if 14<= purchaseTime.hour < 16:
        points += 10
    
    return points

    
@app.route('/receipts/process', methods=["POST"])
def makeId():
    receipt = request.json()
    id = str(uuid.uuid4())
    points = calcPoints(receipt)
    receipts[id] = points
    return jsonify({"id": id})



#should get the points of the specific id
@app.route('/receipts/<id>/process', methods=["POST"])
def returnPoints(id):
    points = receipts.get(id)
    if points is None:
        return(jsonify({'error', 'Receipt not found'})), 404

    return(jsonify({'points', points}))



if __name__ == '__main__':
    app.run(debug=True, port=5000)
