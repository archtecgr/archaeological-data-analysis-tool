import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Number of artifacts
n_artifacts = 150

# Generate sample archaeological data
data = {
    'artifact_id': [f'ART{str(i).zfill(4)}' for i in range(1, n_artifacts + 1)],
    'site': np.random.choice(['Site A', 'Site B', 'Site C', 'Site D', 'Site E'], n_artifacts),
    'excavation_date': [
        (datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1460))).strftime('%Y-%m-%d') 
        for _ in range(n_artifacts)
    ],
    'depth_cm': np.random.uniform(10, 300, n_artifacts).round(2),
    'length_mm': np.random.uniform(20, 500, n_artifacts).round(2),
    'width_mm': np.random.uniform(10, 200, n_artifacts).round(2),
    'weight_g': np.random.uniform(5, 2000, n_artifacts).round(2),
    'material': np.random.choice(['Ceramic', 'Stone', 'Metal', 'Bone', 'Glass'], n_artifacts),
    'period': np.random.choice(['Bronze Age', 'Iron Age', 'Roman', 'Medieval', 'Modern'], n_artifacts),
    'condition': np.random.choice(['Excellent', 'Good', 'Fair', 'Poor'], n_artifacts),
    'x_coordinate': np.random.uniform(0, 1000, n_artifacts).round(2),
    'y_coordinate': np.random.uniform(0, 1000, n_artifacts).round(2),
    'completeness_percent': np.random.uniform(20, 100, n_artifacts).round(1),
    'estimated_age_years': np.random.randint(100, 3000, n_artifacts)
}

# Add some intentional missing values (realistic scenario)
missing_indices = np.random.choice(n_artifacts, size=int(n_artifacts * 0.1), replace=False)
for idx in missing_indices:
    col = np.random.choice(['depth_cm', 'weight_g', 'condition', 'completeness_percent'])
    data[col][idx] = np.nan

# Create DataFrame
df = pd.DataFrame(data)

# Add some duplicates (realistic scenario)
duplicate_rows = df.iloc[[0, 1, 2]].copy()
df = pd.concat([df, duplicate_rows], ignore_index=True)

# Save to CSV
df.to_csv('sample_archaeological_data.csv', index=False)
print(f"Sample archaeological dataset created with {len(df)} artifacts!")
print(f"\nDataset preview:")
print(df.head(10))
print(f"\nDataset info:")
print(df.info())
