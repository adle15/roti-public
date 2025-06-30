from app.enc import AESCipher
from dotenv import load_dotenv
import os

load_dotenv("./db_credential.env",override=True)

class GeminiConfig:
    project = ""
    location = ""
    model = ""
    def __init__(self):
        vertex_location    = os.environ.get('LOCATION')
        vertex_project     = os.environ.get('PROJECT_ID')
        model = os.environ.get('MODEL')
        max_output_token =  int(os.environ.get('MAX_OUTPUT_TOKENS'))
        temperature = float(os.environ.get('TEMPERATURE'))
        top_p = int(os.environ.get('TOP_P'))
        top_k = int(os.environ.get('TOP_K'))#
        similarity_threshold = float(os.environ.get('SIMILARITY_THRESHOLD'))
        similarity_routes_threshold = float(os.environ.get('SIMILARITY_ROUTES_THRESHOLD'))
        max_output_doc = int(os.environ.get('MAX_OUTPUT_DOC'))
        max_output_doc_routes = int(os.environ.get('MAX_OUTPUT_DOC_ROUTES'))
       
        self.vertex_location = vertex_location
        self.vertex_project  = vertex_project
        self.model = model
        self.max_output_token  = max_output_token
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.similarity_routes_threshold = similarity_routes_threshold
        self.max_output_doc = max_output_doc
        self.max_output_doc_routes = max_output_doc_routes

class SaGoogle:
    vertex = ""

    def __init__(self):
        aes = AESCipher('P93233','Lt_03_kenari')
        vertex = aes.decrypt(os.environ.get('VERTEX'))
        
        self.vertex = vertex

class PgCred:
    Instance = ""
    Driver  = ""
    username = ""
    password  = ""
    database = ""
    Type = ""

    def __init__(self):
        sec = AESCipher("P93233", "Lt_03_kenari")

        host = os.environ.get('HOST')
        port = os.environ.get('DB_PORT')
        user = sec.decrypt(os.environ.get('USER'))
        db_name = os.environ.get('DB_NAME')
        password_db = sec.decrypt(os.environ.get('PASSWORD'))
        db_name_semantic_query = os.environ.get('DB_NAME_SEMANTIC_QUERY')

        self.host = host
        self.port  = port
        self.user = user
        self.db_name  = db_name
        self.db_name_semantic_query = db_name_semantic_query
        self.password_db = password_db

class RoleParam:
    where = ""
    def __init__(self):

        where = os.environ.get("RoleIdParam")

        self.where = where