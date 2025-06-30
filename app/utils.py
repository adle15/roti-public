import asyncpg
from pgvector.asyncpg import register_vector
from langchain.docstore.document import Document
from google import genai
import requests
import os

# Your DB information & github token for fetch github profile
db_name = os.getenv('DB_NAME')
user = os.getenv('DB_USERNAME')
password_db = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
github_token = os.getenv('GITHUB_TOKEN')
headers = {
    "Authorization": github_token
}


async def connect_to_db():
     conn = await asyncpg.connect(
        host = host,
        port = port,
        user = user,
        password = password_db,
        database = db_name,
     )

     return conn

async def fetch_github_profile(username):

  user_url = f"https://api.github.com/users/{username}"
  repos_url = f"https://api.github.com/users/{username}/repos"
  user_resp = requests.get(user_url, headers=headers)
  repos_resp = requests.get(repos_url, headers=headers)
  if user_resp.status_code == 200 and repos_resp.status_code == 200:
      user_data = user_resp.json()
      repos_data = repos_resp.json()
      repo_details = []

      for repo in repos_data:
          repo_details.append({
              "Name": repo['name'],
              "URL": repo['html_url'],
              "Description": repo['description'],
              "Language": repo['language'],
              "Stars": repo['stargazers_count'],
              "Forks": repo['forks_count'],
              "Open Issues": repo['open_issues_count'],
              "Created At": repo['created_at'],
              "Last Push": repo['pushed_at']
          })

      profile_info = {
          "Name": user_data.get("name"),
          "Username": user_data.get("login"),
          "Followers": user_data.get("followers"),
          "Following": user_data.get("following"),
          "Public Repos Count": user_data.get("public_repos"),
          "Bio": user_data.get("bio"),
          "Location": user_data.get("location"),
          "Blog": user_data.get("blog"),
          "Profile URL": user_data.get("html_url"),
          "Created At": user_data.get("created_at"),
          "Repositories Info" : repo_details
      }
      return profile_info
  else:
      print("Error fetching data:", user_resp.status_code, repos_resp.status_code)
      return None

async def similarity_search(api_key,prompt,similarity_threshold,num_matches,table_name):
    matches = []

    # embeddings_service = VertexAIEmbeddings(model_name="textembedding-gecko@003",location="asia-southeast1",max_output_tokens=768)
    # qe = embeddings_service.embed_query(prompt)
    client = genai.Client(api_key=api_key)
    embeddings_service = client.models.embed_content(
        model="text-embedding-004",
        contents=prompt)
    
    qe=embeddings_service.embeddings[0].values

    conn = await connect_to_db()

    await register_vector(conn)
    # Find similar products to the query using cosine similarity search
    # over all vector embeddings. This new feature is provided by `pgvector`.
    results = await conn.fetch(
        f"""
                        WITH vector_matches AS (
                          SELECT id, 1 - (embedding <=> $1) AS similarity
                          FROM {table_name}_embeddings
                          WHERE 1 - (embedding <=> $1) > $2
                          ORDER BY similarity DESC
                          LIMIT $3
                        )
                        SELECT
                          nama_file,
                          page_content,
                          page_number,
                          similarity
                        FROM {table_name}
                        JOIN vector_matches ON {table_name}.id=vector_matches.id
                        WHERE {table_name}.id IN (SELECT id FROM vector_matches)
                        ORDER BY similarity DESC
                        """,
      qe,
      similarity_threshold,
      num_matches
    )
    if len(results) == 0:
      return ["Did not find any results. Adjust the query parameters."]
    for r in results:
      # Collect the description for all the matched similar toy products.
      matches.append(Document(page_content=f"""Information:
    {r["page_content"]}.""", metadata={"similarity":r["similarity"], "page_number":r["page_number"]}))
      await conn.close()
    return matches