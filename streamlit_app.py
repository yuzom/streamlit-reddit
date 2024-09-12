import streamlit as st
from google.cloud import firestore
import base64

# Load Firestore credentials from Streamlit secrets
firestore_credentials = st.secrets["firestore"]

# Directly pass the credentials to Firestore without converting to JSON
db = firestore.Client.from_service_account_info(firestore_credentials)

# Streamlit widgets to let a user create or select a folder
st.sidebar.subheader("Folder Management")
folder_path = st.sidebar.text_input("Folder path (e.g., folder/subfolder)", "")

# Button to create the folder if it doesn't exist
if folder_path and st.sidebar.button("Create Folder"):
    # Create an empty document to represent the folder
    db.collection("folders").document(folder_path).set({"type": "folder"})
    st.sidebar.success(f"Folder '{folder_path}' created successfully!")

# File uploader in the selected folder
st.subheader("File Upload")
uploaded_file = st.file_uploader("Upload a file to the folder", type=["png", "jpg", "pdf", "txt", "csv"])

# Enter file metadata like title
title = st.text_input("File title")
submit = st.button("Submit new file")

# Upload the file to the selected folder
if uploaded_file is not None and folder_path and title and submit:
    file_content = uploaded_file.read()

    # Store the file metadata and content in the Firestore under the selected folder
    doc_ref = db.collection("folders").document(folder_path).collection("files").document(title)
    doc_ref.set({
        "title": title,
        "file_name": uploaded_file.name,
        "file_type": uploaded_file.type,
        "file_content": base64.b64encode(file_content).decode("utf-8")
    })

    st.success(f"File '{uploaded_file.name}' uploaded successfully to folder '{folder_path}'!")

# Display folder structure and files within
st.subheader("Folder Structure")

def display_folder_structure(current_folder, indent_level=0):
    # Retrieve subfolders
    folders_ref = db.collection("folders").where("type", "==", "folder")
    subfolders = [folder.id for folder in folders_ref.stream() if folder.id.startswith(current_folder)]
    
    for subfolder in subfolders:
        # Indent to show folder hierarchy
        st.write("    " * indent_level + f"📁 {subfolder}")
        
        # Retrieve files in the current folder
        files_ref = db.collection("folders").document(subfolder).collection("files")
        for doc in files_ref.stream():
            file_data = doc.to_dict()
            file_title = file_data["title"]
            file_name = file_data["file_name"]
            file_type = file_data["file_type"]
            file_content = file_data["file_content"]

            # Indent to match the folder hierarchy
            st.write("    " * (indent_level + 1) + f"📄 {file_name} ({file_type})")
            
            # Display a download button for the file
            b64 = base64.b64decode(file_content)
            st.download_button(f"Download {file_name}", b64, file_name)

# Call the recursive function to display the folder structure
display_folder_structure("")