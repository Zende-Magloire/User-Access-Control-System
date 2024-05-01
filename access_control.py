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
                result_text = f"{record['user'].capitalize()} is allowed to {action} {resource_name}"
            else:
                result_text = f"{record['user'].capitalize()} is not allowed to {action} {resource_name}"
        else:
            result_text = f"{user_name.capitalize()} is not found in the database"

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

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    result_text = None
    if request.method == 'POST':
        user_name = request.form['user_name'].lower()
        roles_input = request.form['roles']
        if not user_name or not roles_input:
            result_text = "User name and roles cannot be empty."
        else:
            with driver.session() as session:
                existing_user = session.run("MATCH (u:User {name: $name}) RETURN COUNT(u) AS count", name=user_name)
                if existing_user.single()["count"] > 0:
                    result_text = f"User '{user_name}' already exists."
                else:
                    roles = [role.strip() for role in roles_input.split(',')]
                    existing_roles = session.run("MATCH (r:Role) RETURN r.name AS name")
                    existing_roles = [record["name"] for record in existing_roles]
                    roles_not_found = [role for role in roles if role not in existing_roles]
                    if roles_not_found:
                        result_text = f"Roles not found in database: {', '.join(roles_not_found)}"
                    else:
                        session.run("CREATE (:User {name: $name})", name=user_name)
                        for role in roles:
                            session.run(
                                """
                                MATCH (user:User {name: $user_name})
                                MATCH (role:Role {name: $role})
                                MERGE (user)-[:HAS_ROLE]->(role)
                                """,
                                user_name=user_name,
                                role=role
                            )
                        result_text = f"User '{user_name}' added successfully."

    return render_template('add_user.html', result=result_text)


if __name__ == '__main__':
    app.run(debug=True)