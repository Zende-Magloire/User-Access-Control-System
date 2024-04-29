from neo4j import GraphDatabase

uri = "neo4j+s://a4aa5801.databases.neo4j.io"
username = "neo4j"
password = "FHoYxcA5XDWYfeKQq2F7HJgtIvsukiyxChVtj2adJ0I"
driver = GraphDatabase.driver(uri, auth=(username, password))

def check_access(user_name, action):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (user:User {name: $user_name})-[:HAS_ROLE]->(role)-[:HAS_POLICY]->(policy)-[:HAS_PERMISSION]->(permission)
            RETURN COUNT(*) > 0 AS allowed
            """,
            user_name=user_name
        )
        record = result.single()
        allowed = record["allowed"]
        if allowed:
            print(f"{user_name} is allowed to {action}.")
        else:
            print(f"{user_name} is not allowed to {action}.")

user_name = input("Enter your name: ")
action = input("Enter the action you want to perform (include the file extension): ")

check_access(user_name, action)

driver.close()


#case sensitive