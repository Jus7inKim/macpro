import streamlit as st
from azure.cosmos import CosmosClient, exceptions

st.title("Azure Cosmos DB RU Check")

# Sidebar for settings
st.sidebar.header("Cosmos DB Settings")
endpoint = st.sidebar.text_input("Endpoint")
key = st.sidebar.text_input("Key", type="password")

if endpoint and key:
    try:
        client = CosmosClient(endpoint, key)
        dbs = list(client.list_databases())
        db_names = [db['id'] for db in dbs]
        database = st.sidebar.selectbox("Database", db_names)
        if database:
            db_client = client.get_database_client(database)
            containers = list(db_client.list_containers())
            container_names = [c['id'] for c in containers]
            container = st.sidebar.selectbox("Container", container_names)
    except Exception as e:
        st.error(f"Connection error: {e}")
        st.stop()
else:
    st.info("Enter endpoint and key to continue.")
    st.stop()

# Query input
st.subheader("Query")
query = st.text_area("Enter SELECT query", "SELECT * FROM c OFFSET 0 LIMIT 10")
submit = st.button("Submit")

if submit and query and container:
    try:
        container_client = db_client.get_container_client(container)
        items = list(container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        st.write("Query Results:", items)
        # RU charge from response headers
        response = container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        ru_charge = response._response.headers.get('x-ms-request-charge')
        st.success(f"RU Charge: {ru_charge}")
    except exceptions.CosmosHttpResponseError as e:
        st.error(f"Query error: {e}")