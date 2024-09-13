from flask import jsonify,render_template,request
from database import app,db,TargetList,TargetUser,TargetListUser
import csv
from io import StringIO


# Route to return the index template
@app.route('/')
def index():
    return render_template('index.html')

# route to return the dict of target lists
@app.route('/app/get_lists/', methods=['GET'])
def get_lists():
    """
    Retrieve all lists from the database.
    """
    target_lists = TargetList.query.all()
    lists = [{"id": target_list.id, "name": target_list.name} for target_list in target_lists]

    return jsonify(lists)

# route to add a new target list to the database
@app.route('/app/add_list/', methods=['POST'])
def add_new_list():
    """
    Add a new list to the database.
    """
    data = request.get_json() 
    new_name = data.get('new_list_name')

    if new_name == '':
        return jsonify({"error": "New name is required"}), 400

    if_name_already_in_use = TargetList.query.filter_by(name=new_name)

    if if_name_already_in_use.first():
        return jsonify({"error": "Name already in use"}),400

    new_list = TargetList(name=new_name)
    db.session.add(new_list)
    db.session.commit()
    return jsonify({"message": "List added successfully"})


# route for deleting a list from the database
@app.route('/app/delete_target_list/<int:list_id>', methods=['DELETE'])
def delete_target_list(list_id):
    """
    Delete a list from the database.
    """
    target_list = TargetList.query.get(list_id)
    if target_list:
        db.session.delete(target_list)
        db.session.commit()
        return jsonify({"message": "List deleted successfully"})
    
    # if target_list was not found, return a message indicating the list was not found
    return jsonify({"error": "List not found"}), 404


# route to rename a target list
@app.route('/app/rename_target_list/<int:list_id>',methods=['UPDATE'])
def rename_target_list(list_id):
    """
    Rename a list in the database.
    """
    target_list = TargetList.query.get(list_id)
    if target_list:
        data = request.get_json()
        new_name = data.get('new_name')
        if new_name == '':
            return jsonify({"error": "New name is required"}), 400

        if_name_already_in_use = TargetList.query.filter_by(name=new_name)

        if if_name_already_in_use.first():
            return jsonify({"error": "Name already in use"}),400
        
        # assign new_name to target_list current name and commit changes
        target_list.name = new_name
        db.session.commit()
        return jsonify({"message": "List renamed successfully"})
            
    # if target_list was not found, return a message indicating the list was not found
    return jsonify({"error": "List not found"}), 404



#route to get all the user per a associated target list
@app.route('/app/get_users/', methods=['GET'])
def get_users():
    """
    Retrieve all users associated with the given list from the database.
    """
    target_lists = TargetList.query.all()
    if not target_lists:
        return jsonify([])
    
    # List of dictionaries to return as JSON
    lists_of_dictionaries = []
    for target_list in target_lists:
        # For each target_list, create a dictionary representation
        list_data = {
            "id": target_list.id,
            "name": target_list.name,
            "users": []
        }

        # Add users to the list data
        for association in target_list.users:
            user = association.target_user  # Access the TargetUser object via the association
            if user:
                list_data["users"].append({
                    "id": user.id,
                    "name": user.name,
                    "surname": user.surname,
                    "email": user.email,
                    "phone": user.phone,
                    "job_position": user.job_position
                })

        lists_of_dictionaries.append(list_data)
    
    return jsonify(lists_of_dictionaries)


#route to add a singe user to the corresponding target list
@app.route('/app/add_user/<int:list_id>', methods=['POST'])
def add_user_to_list(list_id):
    """
    Add a new target user to a target list in the database.
    """
    # Check if the target list exists
    target_list = TargetList.query.get(list_id)
    if not target_list:
        return jsonify({"error": "List not found"}), 404

    data = request.get_json()  # Parse JSON body to access each key
    user_name = data.get('name')
    user_surname = data.get('surname')
    user_email = data.get('email')
    user_phone = data.get('phone')
    user_job_position = data.get('job_position')

    if not user_email:
        return jsonify({"error": "No email provided."}), 400

    # Check if the user is already associated with the target list by filtering their email
    existing_association = db.session.query(TargetListUser).join(TargetUser).filter(
        TargetListUser.target_list_id == list_id,
        TargetUser.email == user_email
    ).first()

    if existing_association:
        return jsonify({"error": f"User with email {user_email} is already added to list {target_list.name}"}), 400

    # Create new TargetUser instance
    new_user = TargetUser(
        name=user_name,
        surname=user_surname,
        email=user_email,
        phone=user_phone,
        job_position=user_job_position
    )
    db.session.add(new_user)
    db.session.flush()  # Get the new user's ID before committing

    # Create a new association between the target user and the target list
    new_association = TargetListUser(
        target_list_id=list_id,
        target_user_id=new_user.id
    )
    db.session.add(new_association)

    # Commit changes to the database
    db.session.commit()

    return jsonify({"message": "User added successfully"}), 200



# route to accept a csv file that contains users information to add to a given list
@app.route('/app/upload_csv/<int:list_id>', methods=['POST'])
def upload_csv(list_id):
    """
    Handle the upload of a CSV file and process it.
    """
    if 'csvFile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['csvFile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the file content as a text stream
        file_content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(file_content))

        # Iterate over each row
        for row in csv_reader:
            email = row.get('Email')
            if email:
                # Check if the user is already added to the target list by filtering their email
                existing_association = db.session.query(TargetListUser).join(TargetUser).filter(
                    TargetListUser.target_list_id == list_id,
                    TargetUser.email == email
                ).first()

                if existing_association:
                    print(f"User with email {email} is already associated with list {list_id}, skipping...")
                    continue  # Skip this user, already added to the target list
                else:
                    # Create new TargetUser instance
                    new_user = TargetUser(
                        name=row.get('\ufeffName') or row.get('Name'), #specific issue with the Name column...
                        surname=row.get('Surname'),
                        email=email,
                        phone=row.get('Phone'),
                        job_position=row.get('Job Position')
                    )
                    db.session.add(new_user)
                    db.session.flush()  # Get the new user's ID before committing

                    # Add association with TargetListUser
                    new_association = TargetListUser(
                        target_list_id=list_id,
                        target_user_id=new_user.id
                    )
                    db.session.add(new_association)
            else:
                print("No email found, skipping row.")

        # Commit all changes at once
        db.session.commit()
        return jsonify({"message": "Users added successfully"}), 200

    return jsonify({"error": "Invalid file type. Only CSV is allowed."}), 400






#route to delete a specific user from the list that the user is part of
@app.route('/app/delete_user_from_list/<int:list_id>/<int:user_id>', methods=['DELETE'])
def delete_user_from_list(list_id, user_id):
    """
    Delete a specific user from a given target list in the database.
    """
    target_list = TargetList.query.get(list_id)
    if not target_list:
        return jsonify({"error": "Target list not found"}), 404

    # Find the TargetListUser association
    target_list_user = TargetListUser.query.filter_by(target_list_id=list_id, target_user_id=user_id).first()

    if not target_list_user:
        return jsonify({"error": "User not found in this list"}), 404
    
    try:
        db.session.delete(target_list_user)
        db.session.commit()
        return jsonify({"message": "User removed from list successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=True)
