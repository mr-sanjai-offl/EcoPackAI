import pandas as pd
import numpy as np
import os

# Ensure data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)

def generate_packaging_data(num_samples=10000):
    np.random.seed(42)
    
    # Generate item dimensions (cm) and weight (kg)
    length = np.random.uniform(5, 100, num_samples)
    width = np.random.uniform(5, 100, num_samples)
    height = np.random.uniform(1, 50, num_samples)
    
    # Sort to ensure L >= W >= H conventionally
    dimensions = np.sort(np.column_stack((length, width, height)), axis=1)[:, ::-1]
    length, width, height = dimensions[:, 0], dimensions[:, 1], dimensions[:, 2]
    
    # Weight somewhat correlated with volume
    volume = length * width * height
    weight = np.random.uniform(0.1, 2.0, num_samples) + (volume / 5000)
    
    # Fragility (categorical)
    fragility = np.random.choice(['Low', 'Medium', 'High'], num_samples, p=[0.6, 0.3, 0.1])
    
    # Determine target: Packaging Type
    packaging_type = []
    for l, w, h, wt, f in zip(length, width, height, weight, fragility):
        vol = l * w * h
        if wt > 15 or l > 80:
            packaging_type.append('Heavy Duty Box')
        elif f == 'High':
            if vol < 5000:
                packaging_type.append('Small Box (Padded)')
            else:
                packaging_type.append('Standard Box (Fragile)')
        elif vol < 2000 and wt < 2:
            packaging_type.append('Padded Mailer')
        elif vol < 10000:
            packaging_type.append('Small Box')
        elif vol < 30000:
            packaging_type.append('Medium Box')
        else:
            packaging_type.append('Large Box')
            
    df = pd.DataFrame({
        'length_cm': length,
        'width_cm': width,
        'height_cm': height,
        'weight_kg': weight,
        'fragility': fragility,
        'packaging_type': packaging_type
    })
    
    # Inject 1% dirty data to simulate real-world logging errors
    noise_indices = np.random.choice(num_samples, size=int(num_samples*0.01), replace=False)
    df.loc[noise_indices, 'weight_kg'] = -np.random.uniform(0.1, 5.0, len(noise_indices))
    
    return df

if __name__ == '__main__':
    print('Generating synthetic packaging data...')
    df = generate_packaging_data(10000)
    output_path = os.path.join(os.path.dirname(__file__), '../data/raw_packaging_data.csv')
    df.to_csv(output_path, index=False)
    print(f'Data successfully saved to {output_path}')
    print('\nFirst 5 rows:')
    print(df.head())
    print('\nClass distribution:')
    print(df['packaging_type'].value_counts())
