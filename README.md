### How to Run the Application Locally after cloning the repo:

1. **Navigate to the root of the `app.py` directory**.
2. **Create and activate a virtual environment to store the required packages**:
   
   - **For Windows**:
     ```bash
     py -m venv name_of_the_venv
     name_of_the_venv\Scripts\activate
     ```

   - **For macOS/Linux**:
     ```bash
     python3 -m venv name_of_the_venv
     source name_of_the_venv/bin/activate
     ```

3. **Install the dependencies from the `requirements.txt` file**:

   
    - **For Windows**:
        ```bash
            pip install -r requirements.txt
        ```

    
    - **For macOS/Linux**
         ```bash
         python -m pip install requirements.txt
         ```
4. **Run the command `python app.py` to run the application.**
5. **Access the link (`http://127.0.0.1:8000`) in any browser.**
<br></br>


### Explanation of the Code within `database.py`

This file defines the database structure for the application using SQLAlchemy with Flask. 
It includes three models: `TargetList`, `TargetUser`, and `TargetListUser`.

1. **`TargetList` Model**:
   - Represents a list of target users.
   - Contains an `id` (primary key) and a `name` (unique, not nullable).
   - Establishes a one-to-many relationship with the `TargetListUser` model to handle associated users.

2. **`TargetUser` Model**:
   - Represents a user that can be associated with multiple target lists.
   - Contains user details: `id`, `name`, `surname`, `email`, `phone`, and `job_position`.
   - Establishes a one-to-many relationship with the `TargetListUser` model to handle multiple list associations.

3. **`TargetListUser` Model**:
   - Establishes a many-to-many relationship between `TargetList` and `TargetUser` models.
   - Contains foreign keys (`target_list_id` and `target_user_id`) to link users and lists.

The `cascade="all, delete-orphan"` option ensures that when a `TargetList` or `TargetUser` is deleted, its associations are also removed automatically.
<br></br>


### Explanation of the Code within `app.py`

#### 1. `@app.route('/', methods=['GET'])`:
- **Purpose:** Returns the index template, which is the main page of the application.

#### 2. `@app.route('/app/get_lists/', methods=['GET'])`:
- **Purpose:** Retrieves all lists from the database and returns them as a JSON response.
- **Process:**
    1. Retrieves all target lists using `TargetList.query.all()`.
    2. Iterates over each list and creates a dictionary containing the list's ID and name.
    3. Returns the list of dictionaries as a JSON response using `jsonify()`.

#### 3. `@app.route('/app/add_list/', methods=['POST'])`:
- **Purpose:** Adds a new list to the database and returns a success message.
- **Process:**
    1. Retrieves the new list name from the request body.
    2. Checks if the list name is empty and returns an error message if it is.
    3. Checks for an existing list with the same name in the database; if found, returns an error message.
    4. Creates a new `TargetList` instance with the provided name.
    5. Adds the new list to the database with `db.session.add()`.
    6. Commits the changes to the database using `db.session.commit()`.
    7. Returns a success message in JSON format.

#### 4. `@app.route('/app/delete_target_list/<int:list_id>', methods=['DELETE'])`:
- **Purpose:** Deletes a list from the database and returns a success message.
- **Process:**
    1. Retrieves the target list using `TargetList.query.get(list_id)`.
    2. If the list is not found, returns a JSON response with an error message.
    3. Deletes the list using `db.session.delete()`.
    4. Commits the changes with `db.session.commit()`.
    5. Returns a success message in JSON format.

#### 5. `@app.route('/app/rename_target_list/<int:list_id>', methods=['PATCH'])`:
- **Purpose:** Renames a list in the database and returns a success message.
- **Process:**
    1. Retrieves the target list using `TargetList.query.get(list_id)`.
    2. If the list is not found, returns an error message.
    3. Retrieves the new list name from the request body.
    4. Checks if the new list name is empty or already exists in the database; if so, returns an error message.
    5. Updates the list's name with the new name.
    6. Commits the changes using `db.session.commit()`.
    7. Returns a success message in JSON format.

#### 6. `@app.route('/app/get_users/', methods=['GET'])`:
- **Purpose:** Retrieves all users associated with each list and returns them as a JSON response.
- **Process:**
    1. Retrieves all target lists using `TargetList.query.all()`.
    2. Iterates over each target list and queries all associated users.
    3. Creates a dictionary for each user containing their ID, name, surname, email, phone, and job position.
    4. Collects all users' dictionaries and appends them to the corresponding list data.
    5. Returns the list data as a JSON response.

#### 7. `@app.route('/app/add_user_to_list/<int:list_id>', methods=['POST'])`:
- **Purpose:** Adds a new user to a specified target list in the database and returns a success message.
- **Process:**
    1. Retrieves the target list using `TargetList.query.get(list_id)`. If not found, returns a JSON response with an error message.
    2. Retrieves the new user's information (name, surname, email, phone, and job position) from the request body. If the email is empty, returns an error message.
    3. Checks if the user is already associated with the target list by filtering the email using `db.session.query(TargetListUser).join(TargetUser).filter()`. If found, returns an error message.
    4. Creates a new `TargetUser` instance with the user's information.
    5. Adds the new user to the database with `db.session.add()`.
    6. Creates an association between the user and the list using the `TargetListUser` model.
    7. Adds this association to the database and commits the changes using `db.session.commit()`.
    8. Returns a success message as a JSON response.

#### 8. `@app.route('/app/upload_csv/<int:list_id>', methods=['POST'])`:
- **Purpose:** Uploads and processes a CSV file containing user information to add users to a specified list.
- **Process:**
    1. Retrieves the target list using `TargetList.query.get(list_id)`. If not found, returns an error message.
    2. Retrieves the CSV file from the request body using `request.files['csvFile']`. If the file is empty or not a `.csv`, returns an error message.
    3. Reads the CSV content as a text stream using `file.read().decode('utf-8')`.
    4. Iterates over each row in the CSV file using `csv.DictReader()`. For each row, retrieves the user's email using `row.get('Email')`. Skips rows with empty emails.
    5. Checks if the user is already associated with the list by filtering the email. If found, skips the user.
    6. Creates a new `TargetUser` instance with the user's information and adds it to the database.
    7. Creates an association between the user and the list using the `TargetListUser` model, adds it to the database, and commits the changes using `db.session.commit()`.
    8. Returns a success message indicating that the users were added.

#### 9. `@app.route('/app/delete_user_from_list/<int:list_id>/<int:user_id>', methods=['DELETE'])`:
- **Purpose:** Deletes a specific user from a given target list in the database and returns a success message.
- **Process:**
    1. Retrieves the target list using `TargetList.query.get(list_id)`. If not found, returns an error message.
    2. Retrieves the user from the list using `TargetListUser.query.filter_by(target_list_id=list_id, target_user_id=user_id)`. If not found, returns an error message.
    3. Deletes the user from the database using `db.session.delete()`.
    4. Commits the changes using `db.session.commit()`.
    5. Returns a success message in JSON format.


#### 10. Run the Application:
-  **Explanation:** 
    1. The if __name__ == '__main__': block ensures the application is only executed when the script is run directly,
    not when it's imported as a module.
    2. The with app.app_context(): db.create_all() block initializes the database by creating the necessary tables before starting the app. This ensures that any changes to the database schema are applied during development.
    3. The app.run(...) command launches the Flask development server with debugging enabled, making it accessible on all network interfaces (host='0.0.0.0') and setting it to run on port 8000. The use_reloader=True option allows the server to automatically reload if there are changes in the code.


    ```python
    if __name__ == '__main__':
        # Create database tables
        with app.app_context():
            db.create_all()
    
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=True)


