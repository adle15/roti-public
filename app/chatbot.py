from google import genai
from pathlib import Path
import os
from pypdf import PdfWriter
from google.genai import types
from PIL import Image
from io import BytesIO
from app.utils import similarity_search, fetch_github_profile

async def generate_content(api_key,prompt,history):

  client = genai.Client(api_key=api_key)
  contents = await similarity_search(api_key,prompt,0.1,10,"content")
  contents = [content.page_content for content in contents]
  final_content = "\n".join(contents)

  formatted_history=''

  if not history:
     formatted_history = 'History Kosong'
  else:
     formatted_history = [
        {
          "row": f"{i+1}",
          "human": history[i]['content'] if history[i]['role'] == 'user' else '',
          "ai": history[i+1]['content'] if i+1 < len(history) and history[i+1]['role'] == 'assistant' else ''
        }
        for i in range(0, len(history))
     ]

  context = f"""
  You are a virtual assistant named Roti🍞 who is assigned to answer questions related to Adli Farhan Ibrahim's career.
  You are provided with information that represents Adli Farhan Ibrahim’s professional experience.
  You can answer in two languages: Bahasa Indonesia and English.
  The prompt may be in English or Bahasa Indonesia—respond according to the language used in the prompt.
  Prompts may be in the form of commands or questions related to the document context.
  Answer comprehensively to ensure the user is helped by your response.
  =============================================================================================================
  prompt : 
  {prompt}
  =============================================================================================================
  information :
  {final_content}
  =============================================================================================================
  history : 
  {formatted_history}
  You are also allowed to use general knowledge to respond to questions beyond the given information.
  If you use your general knowledge, there's no need to mention that you are doing so or say that the information about Adli is not provided.
  Do not mention that your response is based on general knowledge or that Adli’s data is unavailable.
  Answer or summarize in a complete, detailed, informative, friendly, yet professional manner.
  """

  response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents=[context])
  
  return response.text


async def document_analysis(api_key,files,prompt,history):

  saved_file = []

  client = genai.Client(api_key=api_key)

  UPLOAD_DIR = 'uploaded_files'
  Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
  for file in files:
      file_name = file.name
      bytes_data = file.read()
      file_path = os.path.join(UPLOAD_DIR, file_name)
      with open(file_path, "wb") as f:
          f.write(bytes_data)
      saved_file.append(file_path)
  
  merger = PdfWriter()


  for i,p in enumerate(saved_file):
     merger.append(p)

  file_path_merge = os.path.join(UPLOAD_DIR, 'combined_file.pdf')
  merger.write(file_path_merge)
  merger.close()

  sample_file = client.files.upload(file=file_path_merge)

  if not history:
     formatted_history = 'History Kosong'
  else:
     formatted_history = [
        {
          "row": f"{i+1}",
          "human": history[i]['content'] if history[i]['role'] == 'user' else '',
          "ai": history[i+1]['content'] if i+1 < len(history) and history[i+1]['role'] == 'assistant' else ''
        }
        for i in range(0, len(history))
     ]



  context = f"""

  Question:
  {prompt}
  ===============================================================================================================================
  History:
  {formatted_history}
  ===============================================================================================================================
  Instruction:
  You are a virtual assistant named Roti🍞 who is responsible for analyzing a document.
  THE QUESTION MAY BE IN ENGLISH. UNDERSTAND THE LANGUAGE USED IN THE QUESTION ABOVE. ANSWER IN THE SAME LANGUAGE AS THE QUESTION.
  The question may be a command or an inquiry related to the context of the document.
  Answer comprehensively so that the user is well assisted by your response.
  You are provided with context originating from a document file (PDF, DOCX, or DOC), which may consist of more than one document.
  ===============================================================================================================================
  Respond or summarize in a complete, detailed, informative, friendly, yet professional manner.
"""

  final_context = [sample_file] + [context]

  result = client.models.generate_content(
   model="gemini-2.0-flash",
   contents=final_context
  )

  return result.text


async def image_analysis(api_key,files,prompt,history):

  client = genai.Client(api_key=api_key)

  UPLOAD_DIR = 'uploaded_files'
  Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
  file_name = files.name
  bytes_data = files.read()
  file_path = os.path.join(UPLOAD_DIR, file_name)
  with open(file_path, "wb") as f:
      f.write(bytes_data)

  sample_file = client.files.upload(file=file_path)

  if not history:
     formatted_history = 'History Kosong'
  else:
     formatted_history = [
        {
          "row": f"{i+1}",
          "human": history[i]['content'] if history[i]['role'] == 'user' else '',
          "ai": history[i+1]['content'] if i+1 < len(history) and history[i+1]['role'] == 'assistant' else ''
        }
        for i in range(0, len(history))
     ]



  context = f"""

  Question:
  {prompt}
  ===========================================================================================================================
  History:
  {formatted_history}
  ===========================================================================================================================
  Instruction:
  You are a virtual assistant named Roti🍞 who is responsible for analyzing an image.
  THE QUESTION MAY BE IN ENGLISH. DETECT THE LANGUAGE USED IN THE QUESTION ABOVE. RESPOND IN THE SAME LANGUAGE.
  The question may be a command or inquiry related to the context of the image.
  Answer thoroughly so that the user is well assisted by your response.
  You are provided with context originating from an image file (JPG, PNG, etc.), which may include more than one image.
  ===========================================================================================================================
  Respond or summarize in a complete, detailed, informative, friendly, yet professional manner.
"""

  final_context = [sample_file] + [context]

  result = client.models.generate_content(
   model="gemini-2.0-flash",
   contents=final_context
  )

  return result.text

async def image_generation(api_key,files,prompt):
   client = genai.Client(api_key=api_key)

   context = f"""
    You're virtual assistant named Roti🍞. Your duty is generate image from prompt inputed
    by the User.
    ==============================================================================================
    Rule :
    1. You prohibited to generate with anime style (ghibli) like to respect real illustrators, tell the users if they do this.
       Avoid Generated image that can cause copyright issue. Dont Generate the image return it into None Type Object.
    2. You can generate image when human really know it was AI Generated.
    3. Always give description what you're generated
    ==============================================================================================
    Prompt from user:
    {prompt} 
"""
   
   image = None
   
   if files:
    UPLOAD_DIR = 'uploaded_files'
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    file_name = files.name
    bytes_data = files.read()
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(bytes_data)

    sample_file = client.files.upload(file=file_path)
    final_context = [context] + [sample_file]

    response = client.models.generate_content(
      model="gemini-2.0-flash-exp-image-generation",
      contents=final_context,
      config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
      )
    )

    for part in response.candidates[0].content.parts:
     if part.text is not None:
       response = part.text
     elif part.inline_data is not None:
       image = Image.open(BytesIO((part.inline_data.data)))

   else:
    response = client.models.generate_content(
     model="gemini-2.0-flash-exp-image-generation",
     contents=context,
     config=types.GenerateContentConfig(
       response_modalities=['TEXT', 'IMAGE']
     )
    )

    for part in response.candidates[0].content.parts:
     if part.text is not None:
       response = part.text
     elif part.inline_data is not None:
       image = Image.open(BytesIO((part.inline_data.data)))
      
   return response, image

async def roast_github_profile(api_key, username, language):
  
  client = genai.Client(api_key=api_key)
  github_profile = await fetch_github_profile(username)

  context = f"""
  You are a virtual assistant named Roti🍞. Your task is to roast a GitHub profile using the details provided — including bio, name, followers, following, and any other available information.
  Your roast should be harsh, spicy, and unapologetic. The roast must be written in the language specified by the user.
  Just roast directly.
  ================================================================================================
  Github Information : 
  {github_profile}
  ================================================================================================
  Language :
  {language}
"""
  
  result = client.models.generate_content(
   model="gemini-2.0-flash",
   contents=context
  )

  return result.text
  
