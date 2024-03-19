import pandas as pd
from google.cloud import documentai_v1 as documentai

def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    # Instantiates a client
    documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)

    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    # read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

        # load binary data into a document
        raw_document = documentai.RawDocument(
            content=image_content, mime_type=mime_type
        )

        # configure the process request
        request = documentai.ProcessRequest(
            name=resource_name, raw_document=raw_document
        )

        # use the documentAI client to process the request
        result = documentai_client.process_document(request=request)

        return result.document

def trim_text(text: str):
    """
    Remove extra space characters from text (blank, newline, tab, etc.)
    """
    return text.strip().replace("\n", " ")

PROJECT_ID = "document-ai-hebrew"
LOCATION = "us"
PROCESSOR_ID = "150027f8d39135f5"

FILE_PATH = "files\intake-form.pdf"
MIME_TYPE = "application/pdf"

# process the document
document = online_process(
    project_id=PROJECT_ID,
    location=LOCATION,
    processor_id=PROCESSOR_ID,
    file_path=FILE_PATH,
    mime_type=MIME_TYPE,
)

names = []
name_confidence = []
values = []
value_confidence = []

for page in document.pages:
    for field in page.form_fields:
        # Get the extracted field names
        names.append(trim_text(field.field_name.text_anchor.content))
        # Confidence - How "sure" the Model is that the text is correct
        name_confidence.append(field.field_name.confidence)

        values.append(trim_text(field.field_value.text_anchor.content))
        value_confidence.append(field.field_value.confidence)

# create a dataframe from the extracted data
df = pd.DataFrame(
    {
        "Field Name": names,
        "Field Name Confidence": name_confidence,
        "Field Value": values,
        "Field Value Confidence": value_confidence,
    }
)

print(df)