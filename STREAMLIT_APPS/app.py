import streamlit as st
import pandas as pd
import os
from io import BytesIO


st.set_page_config(
    page_title="📀 Data Sweeper",
    layout="wide"
)

st.title("📀 Data Sweeper")
st.write(
    "Transform your files between CSV and Excel formats "
    "with built-in cleaning and visualization."
)


uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel)",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)


if uploaded_files:

    for file in uploaded_files:

        # Get file extension
        file_ext = os.path.splitext(file.name)[-1].lower()


        if file_ext == ".csv":
            df = pd.read_csv(file)

        elif file_ext == ".xlsx":
            df = pd.read_excel(file)

        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue


        st.divider()

        st.subheader(f"📄 {file.name}")

        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

    
        st.subheader("👀 Preview of the File")

        st.dataframe(df.head())


        st.subheader("🧹 Data Cleaning Options")

        clean_data = st.checkbox(
            f"Enable data cleaning for {file.name}",
            key=f"clean_{file.name}"
        )

        if clean_data:

            col1, col2 = st.columns(2)

            # Remove duplicates
            with col1:

                if st.button(
                    "Remove Duplicates",
                    key=f"duplicate_{file.name}"
                ):

                    df.drop_duplicates(inplace=True)

                    st.success(
                        "Duplicates removed successfully."
                    )

            # Fill missing values
            with col2:

                if st.button(
                    "Fill Missing Values",
                    key=f"missing_{file.name}"
                ):

                    numeric_cols = df.select_dtypes(
                        include=["number"]
                    ).columns

                    df[numeric_cols] = df[numeric_cols].fillna(
                        df[numeric_cols].mean()
                    )

                    st.success(
                        "Missing numeric values filled successfully."
                    )

        st.subheader("📋 Select Columns")

        selected_columns = st.multiselect(
            f"Choose columns for {file.name}",
            df.columns.tolist(),
            default=df.columns.tolist(),
            key=f"columns_{file.name}"
        )

        if selected_columns:

            df = df[selected_columns]

            st.write("Selected columns:")

            st.dataframe(df.head())

        else:

            st.warning(
                "Please select at least one column."
            )

        st.subheader("📊 Data Visualization")

        show_visualization = st.checkbox(
            f"Show visualization for {file.name}",
            key=f"visualization_{file.name}"
        )

        if show_visualization:

            numeric_cols = df.select_dtypes(
                include=["number"]
            ).columns.tolist()

            all_cols = df.columns.tolist()

            if len(numeric_cols) >= 1:

                col1, col2 = st.columns(2)

                # X-axis
                with col1:

                    x_axis = st.selectbox(
                        "Select X-axis",
                        all_cols,
                        key=f"x_axis_{file.name}"
                    )

                # Y-axis
                with col2:

                    y_axis = st.selectbox(
                        "Select Y-axis",
                        numeric_cols,
                        key=f"y_axis_{file.name}"
                    )

                # Chart
                st.bar_chart(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            else:

                st.info(
                    "No numeric columns available "
                    "for visualization."
                )

       

        st.subheader("🔄 Conversion Options")

        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel"],
            key=f"conversion_{file.name}"
        )

        if st.button(
            f"Convert {file.name}",
            key=f"convert_{file.name}"
        ):

            buffer = BytesIO()

           
            if conversion_type == "CSV":

                df.to_csv(
                    buffer,
                    index=False
                )

                file_name = (
                    os.path.splitext(file.name)[0]
                    + ".csv"
                )

                mime_type = "text/csv"

           

            else:

                df.to_excel(
                    buffer,
                    index=False
                )

                file_name = (
                    os.path.splitext(file.name)[0]
                    + ".xlsx"
                )

                mime_type = (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )

            # Move pointer to beginning
            buffer.seek(0)

            st.success(
                f"{file.name} converted successfully!"
            )

            
            st.download_button(
                label=f"⬇️ Download {file_name}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
                key=f"download_{file.name}"
            )

    
    st.success("✅ All files processed successfully!")