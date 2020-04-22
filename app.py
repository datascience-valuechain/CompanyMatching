
"""An app to match your list of company names with UK Companies House and extract company numbers first.
"""
import pandas as pd
import difflib
import string
import os
import base64
import pandas as pd
import streamlit as st
from enum import Enum
from io import BytesIO, StringIO
from typing import Union
import pandas as pd
import streamlit as st

st.header("Company Name Matching")



STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

FILE_TYPES = ["csv", "py", "png", "jpg"]


class FileType(Enum):
    """Used to distinguish between file types"""

    IMAGE = "Image"
    CSV = "csv"
    PYTHON = "Python"


def get_file_type(file: Union[BytesIO, StringIO]) -> FileType:
    if isinstance(file, BytesIO):
        return FileType.IMAGE
    content = file.getvalue()
    if (
        content.startswith('"""')
        or "import" in content
        or "from " in content
        or "def " in content
        or "class " in content
        or "print(" in content
    ):
        return FileType.PYTHON

    return FileType.CSV


def preprocess_name(cn):
    cn = cn.lower()
    cn = cn.replace('&','and')
    cn = cn.replace('ltd','')
    cn = cn.replace('limited','')
    cn = cn.replace('.com','')
    cn = cn.replace('p l c','plc')
    cn = cn.replace('the','')
    #cn = cn.replace('company', 'co')
    #cn = cn.replace('technology', '')
    #cn = cn.replace('group', '')
    cn = cn.replace('plc', '')
    cn = cn.replace('llp', '')
    cn = cn.replace('llc', '')
    for c in string.punctuation:
        cn = cn.replace(c," ")
    cn = cn.replace(" ","")
    return cn.strip()

def main():
    """Run this function to display the Streamlit app"""
    st.info(__doc__)
    st.markdown(STYLE, unsafe_allow_html=True)

    file = st.file_uploader("Upload file", type=FILE_TYPES)
    show_file = st.empty()
    if not file:
        show_file.info("Please upload a file of type: " + ", ".join(FILE_TYPES))
        return

    file_type = get_file_type(file)
    if file_type == FileType.IMAGE:
        show_file.image(file)
    elif file_type == FileType.PYTHON:
        st.code(file.getvalue())
    else:
        data = pd.read_csv(file)
        df1 = data
        os.chdir('/Users/staff/Desktop')
        df2 = pd.read_csv("/Users/staff/Desktop/CH_file.csv")
        df1['CompanyName'] = df1['CompanyName'].astype('str')
        df2['CompanyName'] = df2['CompanyName'].astype('str')
        df1['name1'] = [preprocess_name(x) if x == x else '' for x in df1['CompanyName']]
        df2['name1'] = [preprocess_name(x) for x in df2['CompanyName']]
        df1['name'] = df1['name1'].apply(lambda x: difflib.get_close_matches(x, df2['name1'], cutoff = 1.0))
        df3 = pd.merge(df1, df2, left_on = 'name1', right_on = 'name1', how = 'left', indicator = True)
       	st.dataframe(df3.head(10))
        csv = df3.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
        st.markdown(href, unsafe_allow_html=True)

    file.close()


main()






