import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Archaeological Data Analysis Platform",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #8B4513;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A0522D;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #F5F5DC;
        color: #2C241F !important;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #8B4513;
        margin: 1rem 0;
        line-height: 1.5;
    }
    .info-box p {
        color: #2C241F !important;
        margin: 0;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28A745;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'file_name' not in st.session_state:
    st.session_state.file_name = None

# Activity logging function
def log_activity(action, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.activity_log.append({
        'timestamp': timestamp,
        'action': action,
        'details': details
    })

# File download helper
def get_download_link(df, filename, file_format):
    if file_format == "CSV":
        data = df.to_csv(index=False)
        b64 = base64.b64encode(data.encode()).decode()
        ext = "csv"
        mime = "text/csv"
    elif file_format == "Excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        data = output.getvalue()
        b64 = base64.b64encode(data).decode()
        ext = "xlsx"
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:  # JSON
        data = df.to_json(orient='records', indent=2)
        b64 = base64.b64encode(data.encode()).decode()
        ext = "json"
        mime = "application/json"
    
    return f'<a href="data:{mime};base64,{b64}" download="{filename}.{ext}">Download {file_format} file</a>'

# Sidebar
with st.sidebar:
    st.markdown("## 🏺 Archaeological Data Platform")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Overview", "Data Cleaning", "Data Transformation", 
         "Analysis", "Visualization", "Activity Log"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # File upload section
    st.markdown("### Upload Dataset")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'json'],
        help="Upload CSV, Excel, or JSON file"
    )
    
    if uploaded_file is not None:
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            elif file_extension == 'json':
                df = pd.read_json(uploaded_file)
            
            if st.session_state.data is None or st.session_state.file_name != uploaded_file.name:
                st.session_state.data = df
                st.session_state.original_data = df.copy()
                st.session_state.file_name = uploaded_file.name
                log_activity("File Uploaded", f"Loaded {uploaded_file.name} with {len(df)} rows and {len(df.columns)} columns")
                st.success(f"Loaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Dataset info
    if st.session_state.data is not None:
        st.markdown("---")
        st.markdown("### Dataset Info")
        st.info(f"**Rows:** {len(st.session_state.data)}")
        st.info(f"**Columns:** {len(st.session_state.data.columns)}")
        
        # Reset button
        if st.button("Reset to Original", use_container_width=True):
            st.session_state.data = st.session_state.original_data.copy()
            log_activity("Data Reset", "Dataset reset to original state")
            st.rerun()

# Main content area
st.markdown('<div class="main-header">🏺 Archaeological Data Analysis Platform</div>', unsafe_allow_html=True)

# PAGE: OVERVIEW
if page == "Overview":
    st.markdown("## Dataset Overview")
    
    if st.session_state.data is None:
        st.markdown('<div class="info-box">Please upload a dataset using the sidebar to begin analysis.</div>', unsafe_allow_html=True)
        
        # Information about the application
        st.markdown("### About This Application")
        st.write("""
        This platform is designed specifically for archaeological data management and analysis. 
        It provides tools for:
        
        - **Data Cleaning**: Handle missing values, duplicates, and outliers
        - **Data Transformation**: Normalize data and extract features
        - **Statistical Analysis**: Perform correlation analysis and grouping
        - **Visualization**: Create interactive plots and charts
        - **Activity Logging**: Track all operations performed on your data
        """)
        
        st.markdown("### Supported File Formats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("CSV")
        with col2:
            st.info("Excel (XLSX)")
        with col3:
            st.info("JSON")
    
    else:
        # Dataset preview
        st.markdown("### Data Preview")
        st.dataframe(st.session_state.data.head(20), use_container_width=True)
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        st.dataframe(st.session_state.data.describe(), use_container_width=True)
        
        # Data info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Dataset Information")
            info_df = pd.DataFrame({
                'Column': st.session_state.data.columns,
                'Data Type': st.session_state.data.dtypes.values,
                'Non-Null Count': st.session_state.data.count().values,
                'Null Count': st.session_state.data.isnull().sum().values
            })
            st.dataframe(info_df, use_container_width=True)
        
        with col2:
            st.markdown("### Missing Data Visualization")
            missing_data = st.session_state.data.isnull().sum()
            missing_percent = (missing_data / len(st.session_state.data)) * 100
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': missing_percent.values
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
            
            if len(missing_df) > 0:
                fig = px.bar(missing_df, x='Column', y='Missing %', 
                            title='Missing Data Percentage by Column',
                            color='Missing %',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No missing data detected!")

# PAGE: DATA CLEANING
elif page == "Data Cleaning":
    st.markdown("## Data Cleaning")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
    else:
        tabs = st.tabs(["Missing Values", "Duplicates", "Outliers"])
        
        # Tab 1: Missing Values
        with tabs[0]:
            st.markdown("### Handle Missing Values")
            
            missing_cols = st.session_state.data.columns[st.session_state.data.isnull().any()].tolist()
            
            if not missing_cols:
                st.success("No missing values found in the dataset!")
            else:
                st.info(f"Found missing values in {len(missing_cols)} columns")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    selected_col = st.selectbox("Select column to handle", missing_cols)
                    method = st.selectbox(
                        "Select method",
                        ["Drop rows", "Fill with mean", "Fill with median", 
                         "Fill with mode", "Fill with custom value", "Forward fill", "Backward fill"]
                    )
                    
                    if method == "Fill with custom value":
                        custom_value = st.text_input("Enter custom value")
                    
                    if st.button("Apply", type="primary"):
                        before_count = st.session_state.data[selected_col].isnull().sum()
                        
                        if method == "Drop rows":
                            st.session_state.data = st.session_state.data.dropna(subset=[selected_col])
                        elif method == "Fill with mean":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].fillna(
                                st.session_state.data[selected_col].mean())
                        elif method == "Fill with median":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].fillna(
                                st.session_state.data[selected_col].median())
                        elif method == "Fill with mode":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].fillna(
                                st.session_state.data[selected_col].mode()[0])
                        elif method == "Fill with custom value":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].fillna(custom_value)
                        elif method == "Forward fill":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].ffill()
                        elif method == "Backward fill":
                            st.session_state.data[selected_col] = st.session_state.data[selected_col].bfill()
                        
                        after_count = st.session_state.data[selected_col].isnull().sum()
                        log_activity("Missing Values Handled", 
                                   f"Column: {selected_col}, Method: {method}, Before: {before_count}, After: {after_count}")
                        st.success(f"Handled {before_count - after_count} missing values!")
                        st.rerun()
                
                with col2:
                    st.markdown("#### Current Missing Values")
                    missing_df = pd.DataFrame({
                        'Column': missing_cols,
                        'Missing Count': [st.session_state.data[col].isnull().sum() for col in missing_cols],
                        'Percentage': [(st.session_state.data[col].isnull().sum() / len(st.session_state.data)) * 100 
                                      for col in missing_cols]
                    })
                    st.dataframe(missing_df, use_container_width=True)
        
        # Tab 2: Duplicates
        with tabs[1]:
            st.markdown("### Remove Duplicate Rows")
            
            dup_count = st.session_state.data.duplicated().sum()
            
            if dup_count == 0:
                st.success("No duplicate rows found!")
            else:
                st.warning(f"Found {dup_count} duplicate rows ({(dup_count/len(st.session_state.data)*100):.2f}%)")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    keep_option = st.selectbox(
                        "Which duplicate to keep?",
                        ["first", "last", "none"],
                        help="'first': Keep first occurrence, 'last': Keep last occurrence, 'none': Remove all duplicates"
                    )
                    
                    if st.button("Remove Duplicates", type="primary"):
                        before_len = len(st.session_state.data)
                        if keep_option == "none":
                            st.session_state.data = st.session_state.data.drop_duplicates(keep=False)
                        else:
                            st.session_state.data = st.session_state.data.drop_duplicates(keep=keep_option)
                        after_len = len(st.session_state.data)
                        removed = before_len - after_len
                        log_activity("Duplicates Removed", f"Removed {removed} duplicate rows (keep={keep_option})")
                        st.success(f"Removed {removed} duplicate rows!")
                        st.rerun()
                
                with col2:
                    st.markdown("#### Sample Duplicates")
                    duplicates = st.session_state.data[st.session_state.data.duplicated(keep=False)]
                    if len(duplicates) > 0:
                        st.dataframe(duplicates.head(10), use_container_width=True)
        
        # Tab 3: Outliers
        with tabs[2]:
            st.markdown("### Detect and Handle Outliers")
            
            numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns found for outlier detection.")
            else:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    selected_col = st.selectbox("Select column", numeric_cols)
                    method = st.selectbox("Detection method", ["IQR Method", "Z-Score Method"])
                    
                    if method == "Z-Score Method":
                        threshold = st.slider("Z-score threshold", 1.0, 5.0, 3.0, 0.1)
                    
                    # Detect outliers
                    if method == "IQR Method":
                        Q1 = st.session_state.data[selected_col].quantile(0.25)
                        Q3 = st.session_state.data[selected_col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outliers = st.session_state.data[
                            (st.session_state.data[selected_col] < lower_bound) | 
                            (st.session_state.data[selected_col] > upper_bound)
                        ]
                    else:  # Z-Score
                        z_scores = np.abs((st.session_state.data[selected_col] - 
                                          st.session_state.data[selected_col].mean()) / 
                                         st.session_state.data[selected_col].std())
                        outliers = st.session_state.data[z_scores > threshold]
                    
                    st.info(f"Detected {len(outliers)} outliers ({(len(outliers)/len(st.session_state.data)*100):.2f}%)")
                    
                    action = st.selectbox(
                        "Action",
                        ["View only", "Remove outliers", "Cap at boundaries"]
                    )
                    
                    if st.button("Apply Action", type="primary") and action != "View only":
                        before_len = len(st.session_state.data)
                        original_values = st.session_state.data[selected_col].copy()
                        
                        if action == "Remove outliers":
                            if method == "IQR Method":
                                st.session_state.data = st.session_state.data[
                                    (st.session_state.data[selected_col] >= lower_bound) & 
                                    (st.session_state.data[selected_col] <= upper_bound)
                                ]
                            else:
                                st.session_state.data = st.session_state.data[z_scores <= threshold]
                            affected = before_len - len(st.session_state.data)
                            message = f"Rows removed: {affected}"
                        
                        elif action == "Cap at boundaries":
                            if method == "IQR Method":
                                capped_values = st.session_state.data[selected_col].clip(
                                    lower=lower_bound, upper=upper_bound
                                )
                            else:
                                mean_val = st.session_state.data[selected_col].mean()
                                std_val = st.session_state.data[selected_col].std()
                                z_lower = mean_val - (threshold * std_val)
                                z_upper = mean_val + (threshold * std_val)
                                capped_values = st.session_state.data[selected_col].clip(
                                    lower=z_lower, upper=z_upper
                                )
                            changed = int((original_values != capped_values).fillna(False).sum())
                            st.session_state.data[selected_col] = capped_values
                            message = f"Values capped: {changed}"
                        
                        log_activity("Outliers Handled", 
                                   f"Column: {selected_col}, Method: {method}, Action: {action}")
                        st.success(f"Action applied! {message}")
                        st.rerun()
                
                with col2:
                    st.markdown("#### Outlier Visualization")
                    fig = go.Figure()
                    fig.add_trace(go.Box(y=st.session_state.data[selected_col], name=selected_col))
                    fig.update_layout(title=f"Box Plot - {selected_col}", height=400)
                    st.plotly_chart(fig, use_container_width=True)

# PAGE: DATA TRANSFORMATION
elif page == "Data Transformation":
    st.markdown("## Data Transformation")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
    else:
        tabs = st.tabs(["Normalization", "Feature Engineering", "Data Types"])
        
        # Tab 1: Normalization
        with tabs[0]:
            st.markdown("### Normalize Numerical Data")
            
            numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns available for normalization.")
            else:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    selected_cols = st.multiselect("Select columns to normalize", numeric_cols)
                    method = st.selectbox(
                        "Normalization method",
                        ["Min-Max (0-1)", "Z-Score Standardization", "Robust Scaling"]
                    )
                    
                    if st.button("Normalize", type="primary") and selected_cols:
                        successful_cols = []
                        skipped_cols = []
                        
                        for col in selected_cols:
                            series = st.session_state.data[col]
                            
                            if method == "Min-Max (0-1)":
                                min_val = series.min()
                                max_val = series.max()
                                denominator = max_val - min_val
                                if pd.isna(denominator) or denominator == 0:
                                    skipped_cols.append(col)
                                    continue
                                st.session_state.data[f"{col}_normalized"] = (
                                    (series - min_val) / denominator
                                )
                            elif method == "Z-Score Standardization":
                                mean_val = series.mean()
                                std_val = series.std()
                                if pd.isna(std_val) or std_val == 0:
                                    skipped_cols.append(col)
                                    continue
                                st.session_state.data[f"{col}_standardized"] = (
                                    (series - mean_val) / std_val
                                )
                            elif method == "Robust Scaling":
                                median_val = series.median()
                                q75, q25 = series.quantile([0.75, 0.25])
                                iqr = q75 - q25
                                if pd.isna(iqr) or iqr == 0:
                                    skipped_cols.append(col)
                                    continue
                                st.session_state.data[f"{col}_robust"] = (
                                    (series - median_val) / iqr
                                )
                            successful_cols.append(col)
                        
                        if successful_cols:
                            log_activity("Data Normalized", f"Columns: {', '.join(successful_cols)}, Method: {method}")
                            st.success(f"Normalized {len(successful_cols)} columns!")
                        if skipped_cols:
                            st.warning(
                                "Skipped columns with no variation (constant values or insufficient numeric data): "
                                + ", ".join(skipped_cols)
                            )
                        if successful_cols or skipped_cols:
                            st.rerun()
                
                with col2:
                    if selected_cols:
                        st.markdown("#### Before Normalization")
                        st.dataframe(
                            st.session_state.data[selected_cols].describe(),
                            use_container_width=True
                        )
        
        # Tab 2: Feature Engineering
        with tabs[1]:
            st.markdown("### Feature Engineering")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Date Feature Extraction")
                # Only expose columns that contain enough values that can be
                # interpreted as dates. This prevents identifiers such as
                # artifact_id from being treated as dates by accident.
                candidate_cols = st.session_state.data.select_dtypes(
                    include=['object', 'datetime64', 'datetime64[ns]']
                ).columns.tolist()
                date_cols = []
                for candidate in candidate_cols:
                    if pd.api.types.is_datetime64_any_dtype(st.session_state.data[candidate]):
                        date_cols.append(candidate)
                    else:
                        parsed = pd.to_datetime(
                            st.session_state.data[candidate], errors='coerce'
                        )
                        non_null = st.session_state.data[candidate].notna().sum()
                        if non_null > 0 and (parsed.notna().sum() / non_null) >= 0.8:
                            date_cols.append(candidate)
                
                if date_cols:
                    selected_date_col = st.selectbox("Select date column", date_cols)
                    
                    features_to_extract = st.multiselect(
                        "Select features to extract",
                        ["Year", "Month", "Day", "Day of Week", "Quarter", "Is Weekend"]
                    )
                    
                    if st.button("Extract Features", type="primary") and features_to_extract:
                        try:
                            # Convert to datetime if not already
                            date_series = pd.to_datetime(st.session_state.data[selected_date_col], errors='coerce')
                            
                            if "Year" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_year"] = date_series.dt.year
                            if "Month" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_month"] = date_series.dt.month
                            if "Day" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_day"] = date_series.dt.day
                            if "Day of Week" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_dayofweek"] = date_series.dt.dayofweek
                            if "Quarter" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_quarter"] = date_series.dt.quarter
                            if "Is Weekend" in features_to_extract:
                                st.session_state.data[f"{selected_date_col}_is_weekend"] = (
                                    date_series.dt.dayofweek >= 5
                                ).astype(int)
                            
                            log_activity("Features Extracted", 
                                       f"Column: {selected_date_col}, Features: {', '.join(features_to_extract)}")
                            st.success("Features extracted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("No suitable date columns found.")
            
            with col2:
                st.markdown("#### Create New Features")
                
                numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) >= 2:
                    col_a = st.selectbox("First column", numeric_cols, key="feat_col_a")
                    operation = st.selectbox("Operation", ["+", "-", "*", "/", "ratio"])
                    col_b = st.selectbox("Second column", numeric_cols, key="feat_col_b")
                    new_col_name = st.text_input("New column name", value=f"{col_a}_{operation}_{col_b}")
                    
                    if st.button("Create Feature", type="primary"):
                        try:
                            if operation == "+":
                                st.session_state.data[new_col_name] = (
                                    st.session_state.data[col_a] + st.session_state.data[col_b]
                                )
                            elif operation == "-":
                                st.session_state.data[new_col_name] = (
                                    st.session_state.data[col_a] - st.session_state.data[col_b]
                                )
                            elif operation == "*":
                                st.session_state.data[new_col_name] = (
                                    st.session_state.data[col_a] * st.session_state.data[col_b]
                                )
                            elif operation == "/":
                                denominator = st.session_state.data[col_b].replace(0, np.nan)
                                st.session_state.data[new_col_name] = (
                                    st.session_state.data[col_a] / denominator
                                )
                            elif operation == "ratio":
                                denominator = st.session_state.data[col_b].replace(0, np.nan)
                                st.session_state.data[new_col_name] = (
                                    st.session_state.data[col_a] / denominator
                                )
                            
                            log_activity("Feature Created", f"{new_col_name} = {col_a} {operation} {col_b}")
                            st.success(f"Created feature: {new_col_name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # Tab 3: Data Types
        with tabs[2]:
            st.markdown("### Convert Data Types")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                all_cols = st.session_state.data.columns.tolist()
                selected_col = st.selectbox("Select column", all_cols)
                current_type = st.session_state.data[selected_col].dtype
                
                st.info(f"Current type: {current_type}")
                
                new_type = st.selectbox(
                    "Convert to",
                    ["int", "float", "string", "datetime", "category"]
                )
                
                if st.button("Convert", type="primary"):
                    try:
                        original_series = st.session_state.data[selected_col].copy()
                        converted_series = None
                        invalid_count = 0
                        
                        if new_type == "int":
                            numeric_series = pd.to_numeric(original_series, errors='coerce')
                            # Archaeological identifiers such as ART0001 are common in
                            # artifact catalogues. If a string contains a numeric suffix,
                            # preserve that identifier as its numeric component instead of
                            # converting every value to missing.
                            if numeric_series.notna().sum() == 0 and original_series.dtype == object:
                                extracted = original_series.astype('string').str.extract(r'(\d+)')[0]
                                numeric_series = pd.to_numeric(extracted, errors='coerce')
                            invalid_count = int(original_series.notna().sum() - numeric_series.notna().sum())
                            converted_series = numeric_series.astype('Int64')
                        elif new_type == "float":
                            converted_series = pd.to_numeric(original_series, errors='coerce')
                            invalid_count = int(original_series.notna().sum() - converted_series.notna().sum())
                        elif new_type == "string":
                            converted_series = original_series.astype('string')
                        elif new_type == "datetime":
                            converted_series = pd.to_datetime(original_series, errors='coerce')
                            invalid_count = int(original_series.notna().sum() - converted_series.notna().sum())
                        elif new_type == "category":
                            converted_series = original_series.astype('category')
                        
                        if invalid_count > 0 and new_type in ["int", "float", "datetime"]:
                            st.warning(
                                f"{invalid_count} non-null values could not be converted and would become missing."
                            )
                        
                        st.session_state.data[selected_col] = converted_series
                        log_activity("Data Type Converted", f"{selected_col}: {current_type} → {new_type}")
                        st.success(f"Converted {selected_col} to {new_type}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                st.markdown("#### All Column Types")
                type_df = pd.DataFrame({
                    'Column': st.session_state.data.columns,
                    'Data Type': st.session_state.data.dtypes.values
                })
                st.dataframe(type_df, use_container_width=True, height=400)

# PAGE: ANALYSIS
elif page == "Analysis":
    st.markdown("## Statistical Analysis")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
    else:
        tabs = st.tabs(["Correlation Analysis", "Group Analysis", "Statistical Summary"])
        
        # Tab 1: Correlation Analysis
        with tabs[0]:
            st.markdown("### Correlation Analysis")
            
            numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) < 2:
                st.warning("Need at least 2 numeric columns for correlation analysis.")
            else:
                selected_cols = st.multiselect(
                    "Select columns for correlation",
                    numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))]
                )
                
                if selected_cols and len(selected_cols) >= 2:
                    correlation_matrix = st.session_state.data[selected_cols].corr()
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("#### Correlation Matrix")
                        st.dataframe(correlation_matrix.style.background_gradient(cmap='coolwarm', axis=None),
                                   use_container_width=True)
                    
                    with col2:
                        st.markdown("#### Heatmap")
                        fig = px.imshow(
                            correlation_matrix,
                            labels=dict(color="Correlation"),
                            x=correlation_matrix.columns,
                            y=correlation_matrix.columns,
                            color_continuous_scale='RdBu_r',
                            aspect="auto"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Strong correlations
                    st.markdown("#### Strong Correlations (|r| > 0.7)")
                    strong_corr = []
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            corr_val = correlation_matrix.iloc[i, j]
                            if abs(corr_val) > 0.7:
                                strong_corr.append({
                                    'Variable 1': correlation_matrix.columns[i],
                                    'Variable 2': correlation_matrix.columns[j],
                                    'Correlation': corr_val
                                })
                    
                    if strong_corr:
                        st.dataframe(pd.DataFrame(strong_corr), use_container_width=True)
                    else:
                        st.info("No strong correlations found (|r| > 0.7)")
        
        # Tab 2: Group Analysis
        with tabs[1]:
            st.markdown("### Group Analysis")
            
            categorical_cols = st.session_state.data.select_dtypes(
                include=['object', 'category']
            ).columns.tolist()
            numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not categorical_cols or not numeric_cols:
                st.warning("Need both categorical and numeric columns for group analysis.")
            else:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    group_col = st.selectbox("Group by", categorical_cols)
                    value_col = st.selectbox("Analyze", numeric_cols)
                    agg_functions = st.multiselect(
                        "Aggregation functions",
                        ["mean", "median", "sum", "count", "min", "max", "std"],
                        default=["mean", "count"]
                    )
                
                if st.button("Analyze Groups", type="primary"):
                    grouped = st.session_state.data.groupby(group_col)[value_col].agg(agg_functions)
                    
                    st.markdown("#### Results")
                    st.dataframe(grouped, use_container_width=True)
                    
                    # Visualization
                    st.markdown("#### Visualization")
                    if "mean" in agg_functions:
                        fig = px.bar(
                            grouped.reset_index(),
                            x=group_col,
                            y="mean",
                            title=f"Mean {value_col} by {group_col}",
                            labels={"mean": f"Mean {value_col}"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        # Tab 3: Statistical Summary
        with tabs[2]:
            st.markdown("### Statistical Summary")
            
            numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns for statistical summary.")
            else:
                selected_col = st.selectbox("Select column", numeric_cols)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Mean", f"{st.session_state.data[selected_col].mean():.2f}")
                    st.metric("Median", f"{st.session_state.data[selected_col].median():.2f}")
                    st.metric("Mode", f"{st.session_state.data[selected_col].mode()[0]:.2f}")
                
                with col2:
                    st.metric("Std Dev", f"{st.session_state.data[selected_col].std():.2f}")
                    st.metric("Variance", f"{st.session_state.data[selected_col].var():.2f}")
                    st.metric("Range", f"{st.session_state.data[selected_col].max() - st.session_state.data[selected_col].min():.2f}")
                
                with col3:
                    st.metric("Min", f"{st.session_state.data[selected_col].min():.2f}")
                    st.metric("Max", f"{st.session_state.data[selected_col].max():.2f}")
                    st.metric("Count", f"{st.session_state.data[selected_col].count()}")
                
                # Distribution plot
                st.markdown("#### Distribution")
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=st.session_state.data[selected_col], name=selected_col))
                fig.update_layout(title=f"Distribution of {selected_col}", height=400)
                st.plotly_chart(fig, use_container_width=True)

# PAGE: VISUALIZATION
elif page == "Visualization":
    st.markdown("## Data Visualization")
    
    if st.session_state.data is None:
        st.warning("Please upload a dataset first.")
    else:
        viz_type = st.selectbox(
            "Select visualization type",
            ["Distribution Plot", "Box Plot", "Scatter Plot", "Bar Chart", 
             "Line Chart", "Heatmap", "Pie Chart"]
        )
        
        numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = st.session_state.data.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        
        # Distribution Plot
        if viz_type == "Distribution Plot":
            if numeric_cols:
                col = st.selectbox("Select column", numeric_cols)
                bins = st.slider("Number of bins", 10, 100, 30)
                
                fig = px.histogram(
                    st.session_state.data,
                    x=col,
                    nbins=bins,
                    title=f"Distribution of {col}",
                    marginal="box"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns available.")
        
        # Box Plot
        elif viz_type == "Box Plot":
            if numeric_cols:
                cols_to_plot = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:3])
                
                if cols_to_plot:
                    fig = go.Figure()
                    for col in cols_to_plot:
                        fig.add_trace(go.Box(y=st.session_state.data[col], name=col))
                    fig.update_layout(title="Box Plot Comparison", height=500)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns available.")
        
        # Scatter Plot
        elif viz_type == "Scatter Plot":
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols)
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1))
                
                color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols)
                
                if color_col == "None":
                    fig = px.scatter(st.session_state.data, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                else:
                    fig = px.scatter(st.session_state.data, x=x_col, y=y_col, color=color_col,
                                   title=f"{y_col} vs {x_col} (colored by {color_col})")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns.")
        
        # Bar Chart
        elif viz_type == "Bar Chart":
            if categorical_cols and numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    cat_col = st.selectbox("Category", categorical_cols)
                with col2:
                    val_col = st.selectbox("Value", numeric_cols)
                
                agg_func = st.selectbox("Aggregation", ["mean", "sum", "count", "median"])
                
                grouped_data = st.session_state.data.groupby(cat_col)[val_col].agg(agg_func).reset_index()
                
                fig = px.bar(grouped_data, x=cat_col, y=val_col, 
                           title=f"{agg_func.capitalize()} of {val_col} by {cat_col}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need both categorical and numeric columns.")
        
        # Line Chart
        elif viz_type == "Line Chart":
            if len(numeric_cols) >= 1:
                x_col = st.selectbox("X-axis", st.session_state.data.columns.tolist())
                y_cols = st.multiselect("Y-axis (can select multiple)", numeric_cols, default=[numeric_cols[0]])
                
                if y_cols:
                    fig = go.Figure()
                    for col in y_cols:
                        fig.add_trace(go.Scatter(x=st.session_state.data[x_col], 
                                               y=st.session_state.data[col], 
                                               mode='lines+markers', 
                                               name=col))
                    fig.update_layout(title="Line Chart", height=500)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns available.")
        
        # Heatmap
        elif viz_type == "Heatmap":
            if len(numeric_cols) >= 2:
                selected_cols = st.multiselect("Select columns", numeric_cols, 
                                              default=numeric_cols[:min(10, len(numeric_cols))])
                
                if len(selected_cols) >= 2:
                    corr_matrix = st.session_state.data[selected_cols].corr()
                    
                    fig = px.imshow(corr_matrix,
                                  labels=dict(color="Correlation"),
                                  x=corr_matrix.columns,
                                  y=corr_matrix.columns,
                                  color_continuous_scale='RdBu_r',
                                  aspect="auto",
                                  title="Correlation Heatmap")
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns.")
        
        # Pie Chart
        elif viz_type == "Pie Chart":
            if categorical_cols:
                col = st.selectbox("Select column", categorical_cols)
                
                value_counts = st.session_state.data[col].value_counts()
                
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"Distribution of {col}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No categorical columns available.")

# PAGE: ACTIVITY LOG
elif page == "Activity Log":
    st.markdown("## Activity Log")
    
    if not st.session_state.activity_log:
        st.info("No activities logged yet. Start working with your data!")
    else:
        # Display log
        log_df = pd.DataFrame(st.session_state.activity_log)
        st.dataframe(log_df, use_container_width=True, height=400)
        
        # Export options
        st.markdown("### Export Options")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("Clear Log", type="secondary"):
                st.session_state.activity_log = []
                st.rerun()
        
        with col2:
            log_csv = log_df.to_csv(index=False)
            st.download_button(
                "Download Log",
                data=log_csv,
                file_name="activity_log.csv",
                mime="text/csv"
            )
        
        with col3:
            if st.session_state.data is not None:
                csv_link = get_download_link(st.session_state.data, "processed_data", "CSV")
                st.markdown(csv_link, unsafe_allow_html=True)
        
        with col4:
            if st.session_state.data is not None:
                excel_link = get_download_link(st.session_state.data, "processed_data", "Excel")
                st.markdown(excel_link, unsafe_allow_html=True)
        
        with col5:
            if st.session_state.data is not None:
                json_link = get_download_link(st.session_state.data, "processed_data", "JSON")
                st.markdown(json_link, unsafe_allow_html=True)
        
        # Statistics
        st.markdown("### Session Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Activities", len(st.session_state.activity_log))
        
        with col2:
            if st.session_state.data is not None and st.session_state.original_data is not None:
                rows_changed = len(st.session_state.original_data) - len(st.session_state.data)
                st.metric("Rows Changed", rows_changed)
        
        with col3:
            if st.session_state.data is not None and st.session_state.original_data is not None:
                cols_changed = len(st.session_state.data.columns) - len(st.session_state.original_data.columns)
                st.metric("Columns Changed", cols_changed)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🏺 Archaeological Data Analysis Platform | "
    "Built with Streamlit</div>",
    unsafe_allow_html=True
)