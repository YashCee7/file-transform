import pandas as pd
from datetime import datetime
import streamlit as st
from io import BytesIO
# us, met  - AMER
# my, hk, au - ASIA
# tr, fr, pl - EMEA
# ending with jp - JAPAN 
# aging in days


st.title("File Transformer")
st.text("File Input:")
file = st.file_uploader("Upload your CSV File here", type = ["csv"])
if file is not None:
    severity_flag,region_flag,aging_flag = False,False,False
    df = pd.read_csv(file)

    # Severity
    if df['Risk Score']:
        severity_flag = True
        df['Severity'] = ''
        df['Severity'] = df['Risk Score'].apply(lambda x: 'High' if x >= 67 else 'Medium')
        severity = df.pop('Severity')
        df.insert(1, 'Severity', severity)

    # Region
    if df['Asset Hostname']:
        region_flag = True
        def regionFinder(s):
            try:
                if s.startswith('us') or s.startswith('met'):
                    return 'AMER'
                elif s.startswith('my') or s.startswith('hk') or s.startswith('au'):
                    return 'ASIA'
                elif s.startswith('tr') or s.startswith('fr') or s.startswith('pl'):
                    return 'EMEA'
                elif s.endswith('jp'):
                    return 'JAPAN'
            except BaseException:
                pass
        df['Region'] = df['Asset Hostname'].apply(regionFinder)
        region = df.pop('Region')
        df.insert(10, 'Region', region)

    # Aging
    if df['Last Seen'] and df['Found']:
        aging_flag = True
        def dateDifference(date1, date2):
            if date1 == '' or date2 == '':
                return 0
            date_format = '%Y-%m-%d'
            date1 = datetime.strptime(date1, date_format)
            date2 = datetime.strptime(date2, date_format)
            diff = date2 - date1
            return diff.days

        df['Last Seen'] = df['Last Seen'].apply(lambda x: x[:x.index('T')] if isinstance(x, str) else '')
        df['Found'] = df['Found'].apply(lambda x: x[:x.index('T')] if isinstance(x, str) else '')
        df['Aging'] = ''
        rowIndex = 0
        for date1, date2 in zip(df['Found'], df['Last Seen']):
            df.loc[rowIndex, 'Aging'] = dateDifference(date1, date2)
            rowIndex += 1
        aging = df.pop('Aging')
        df.insert(7, 'Aging', aging)

        if any([severity_flag, region_flag, aging_flag]):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine = "xlsxwriter") as writer:
                df.to_excel(writer, index=False)
            transformed_file = buffer.getvalue()
            if st.download_button(label = "Download your transformed file here", data = transformed_file, 
                            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
                st.success("thank you for using this app")
                st.stop()
        else:
            st.text("the file provided does not have any columns which need to be processed.")
            st.stop()