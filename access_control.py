from flask import Flask, render_template, request
from neo4j import GraphDatabase

app = Flask(__name__)

uri = "neo4j+s://a4aa5801.databases.neo4j.io"
username = "neo4j"
password = "FHoYxcA5XDWYfeKQq2F7HJgtIvsukiyxChVtj2adJ0I"
driver = GraphDatabase.driver(uri, auth=(username, password))

def check_access(user_name, action, resource_name):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (user:User {name: $user_name})-[:HAS_ROLE]->(role:Role)-[:HAS_POLICY]->(policy)-[:CAN_READ|CAN_WRITE|CAN_CREATE|CAN_DELETE]->(resource:Resource {name: $resource_name})
            RETURN user.name AS user, role.name AS role, policy.name AS policy, resource.name AS resource, $action AS action, COUNT(*) > 0 AS allowed
            """,
            user_name=user_name,
            resource_name=resource_name,
            action=action.upper()
        )
        record = result.single()

        if record:
            allowed = record["allowed"]
            if allowed:
                result_text = f"{record['user']} is allowed to {action} {resource_name}"
            else:
                result_text = f"{record['user']} is not allowed to {action} {resource_name}"
        else:
            result_text = f"{user_name.capitalize()} is not allowed to {action} {resource_name}"

    return result_text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form['user_name'].lower()
        action = request.form['action'].lower()
        resource_name = request.form['resource_name']
        result = check_access(user_name, action, resource_name)
        return render_template('result.html', result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
