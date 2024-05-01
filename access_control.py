from neo4j import GraphDatabase

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
                print(f"{record['user']} is allowed to {action} {resource_name}")
            else:
                print(f"{record['user']} is not allowed to {action} {resource_name}")
        else:
            print(f"{user_name.capitalize()} is not allowed to {action} {resource_name}")

        # if record:
        #     print(f"User: {record['user']}, Role: {record['role']}, Policy: {record['policy']}, Resource: {record['resource']}, Action: {record['action']}, Allowed: {allowed}")

user_name = input("Enter your name: ").lower()
action = input("Enter the action you want to perform (e.g., read, write, delete): ").lower()
resource_name = input("Enter the resource name (including the file extension): ")

check_access(user_name, action, resource_name)




driver.close()