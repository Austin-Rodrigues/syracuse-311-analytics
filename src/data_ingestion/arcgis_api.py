"""
Syracuse 311 (SYRCityline) Data API Client
Connects to ArcGIS REST API to fetch service request data

IMPORTANT: This module ONLY fetches raw data from the API.
All data cleaning and transformation happens in data_processing/ modules.

Raw Field Reference:
- Id: Request ID
- Category: Request type category
- Summary: Brief description
- Description: Full description
- Address: Location
- Lat, Lng: Coordinates (WGS84)
- Created_at_local: Creation timestamp (STRING - needs parsing in pipeline)
- Acknowledged_at_local: Acknowledgment timestamp (STRING)
- Closed_at_local: Closure timestamp (STRING)
- Minutes_to_Acknowledge: Time to first response (NUMERIC)
- Minutes_to_Close: Time to resolution (STRING - needs conversion in pipeline)
- Agency_Name: Responsible department
- Rating: User satisfaction rating
- Request_type: Numeric type code
- Sla_in_hours: Service level agreement target
- Report_Source: How request was submitted
"""

import requests
import pandas as pd
import json
from datetime import datetime
from typing import Optional, Dict, List
import time
import os


class SyracuseDataAPI:
    """
    Client for accessing Syracuse Open Data via ArcGIS REST API

    This class ONLY handles API communication and basic data extraction.
    No data cleaning or transformation is performed here.
    """

    BASE_URL = "https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/SYRCityline_Requests_2021_Present/FeatureServer/0/query"

    def __init__(self, timeout: int = 30):
        """
        Initialize the API client

        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self._field_names = None

    def _make_request(self, params: Dict) -> Dict:
        """
        Make a request to the ArcGIS API

        Args:
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_field_info(self) -> List[Dict]:
        """
        Get metadata about available fields in the dataset

        Returns:
            List of field definitions with names, types, and descriptions
        """
        metadata_url = self.BASE_URL.replace('/query', '')

        try:
            response = self.session.get(
                metadata_url,
                params={'f': 'json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            fields = data.get('fields', [])

            print(f"\n=== Available fields: {len(fields)} ===")
            for field in fields:
                print(f"  - {field['name']} ({field['type']})")

            self._field_names = [f['name'] for f in fields]
            return fields

        except Exception as e:
            print(f"Could not fetch field info: {e}")
            return []

    def fetch_records(
        self,
        limit: int = 1000,
        offset: int = 0,
        where_clause: str = "1=1",
        fields: Optional[List[str]] = None,
        return_geometry: bool = False,
        order_by: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch raw service request records from the API

        IMPORTANT: Returns RAW data exactly as provided by API.
        No cleaning or transformation is performed.

        Args:
            limit: Maximum number of records to fetch (max 2000 per request)
            offset: Starting record position for pagination
            where_clause: SQL-like WHERE clause (default: "1=1" fetches all)
            fields: List of field names to retrieve (None = all fields)
            return_geometry: Include geometric data (not typically needed)
            order_by: Field to order results by (e.g., 'ObjectId DESC')

        Returns:
            DataFrame with RAW service request data
        """
        params = {
            'where': where_clause,
            'outFields': ','.join(fields) if fields else '*',
            'returnGeometry': str(return_geometry).lower(),
            'f': 'json',
            'resultOffset': offset,
            'resultRecordCount': min(limit, 2000),
        }

        if order_by:
            params['orderByFields'] = order_by

        print(f"Fetching records {offset} to {offset + limit}...")

        data = self._make_request(params)

        if 'error' in data:
            error_msg = data['error']
            print(f"\nAPI Error: {error_msg}")
            raise Exception(f"API Error: {error_msg}")

        features = data.get('features', [])

        if not features:
            print("No records found.")
            return pd.DataFrame()

        # Extract attributes from features
        records = [feature.get('attributes', {}) for feature in features]
        df = pd.DataFrame(records)

        print(f"✓ Retrieved {len(df)} raw records")

        return df

    def fetch_all_records(
        self,
        batch_size: int = 2000,
        max_records: Optional[int] = None,
        where_clause: str = "1=1",
        save_raw: bool = False,
        output_dir: str = "data/raw"
    ) -> pd.DataFrame:
        """
        Fetch all records using pagination

        Args:
            batch_size: Records per batch (max 2000)
            max_records: Maximum total records to fetch (None = all)
            where_clause: SQL-like WHERE clause
            save_raw: If True, save each batch to disk as fetched
            output_dir: Directory to save raw data (if save_raw=True)

        Returns:
            DataFrame with all fetched RAW records
        """
        all_data = []
        offset = 0
        batch_num = 0

        if save_raw:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Raw data will be saved to: {output_dir}")

        print(f"Starting batch download (batch_size={batch_size})...")

        while True:
            df_batch = self.fetch_records(
                limit=batch_size,
                offset=offset,
                where_clause=where_clause
            )

            if df_batch.empty:
                break

            all_data.append(df_batch)

            # Save raw batch if requested
            if save_raw:
                batch_file = os.path.join(
                    output_dir,
                    f"raw_batch_{batch_num:04d}.csv"
                )
                df_batch.to_csv(batch_file, index=False)
                print(f"  Saved raw batch to {batch_file}")

            offset += len(df_batch)
            batch_num += 1

            if max_records and offset >= max_records:
                print(f"Reached max_records limit ({max_records})")
                break

            if len(df_batch) < batch_size:
                break

            # Be nice to the API
            time.sleep(0.5)

        if not all_data:
            return pd.DataFrame()

        df_combined = pd.concat(all_data, ignore_index=True)
        print(f"\n✓ Total raw records fetched: {len(df_combined)}")

        # Add metadata about extraction
        df_combined.attrs['extraction_timestamp'] = datetime.now().isoformat()
        df_combined.attrs['total_records'] = len(df_combined)

        return df_combined

    def fetch_recent(self, days: int = 30) -> pd.DataFrame:
        """
        Fetch raw service requests from the last N days

        Args:
            days: Number of days to look back

        Returns:
            DataFrame with RAW recent records
        """
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        date_str = cutoff_date.strftime('%Y-%m-%d')

        where_clause = f"Created_at_local >= '{date_str}'"

        print(f"Fetching requests from last {days} days (since {date_str})...")
        return self.fetch_all_records(where_clause=where_clause)

    def save_raw_data(
        self,
        df: pd.DataFrame,
        filename: str = None,
        output_dir: str = "data/raw"
    ) -> str:
        """
        Save raw data with metadata

        Args:
            df: DataFrame to save
            filename: Output filename (default: auto-generated with timestamp)
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"syracuse_311_raw_{timestamp}.csv"

        filepath = os.path.join(output_dir, filename)

        # Save the data
        df.to_csv(filepath, index=False)

        # Save metadata
        metadata = {
            'extraction_timestamp': datetime.now().isoformat(),
            'record_count': len(df),
            'columns': df.columns.tolist(),
            'date_range': {
                'min': str(df['Created_at_local'].min()) if 'Created_at_local' in df.columns else None,
                'max': str(df['Created_at_local'].max()) if 'Created_at_local' in df.columns else None
            }
        }

        metadata_file = filepath.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved raw data to: {filepath}")
        print(f"✓ Saved metadata to: {metadata_file}")

        return filepath


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Syracuse 311 Data API Client - Raw Data Extraction")
    print("=" * 70)

    api = SyracuseDataAPI()

    # Get field information
    print("\n" + "=" * 70)
    print("Available Fields (Raw Schema):")
    print("=" * 70)
    fields = api.get_field_info()

    # Fetch sample raw data
    print("\n" + "=" * 70)
    print("Fetching 100 sample records (RAW)...")
    print("=" * 70)

    df_raw = api.fetch_records(limit=100)

    if not df_raw.empty:
        print(f"\n✓ Retrieved {len(df_raw)} raw records")
        print(f"\nDataset shape: {df_raw.shape}")
        print(f"\nColumn names (raw):")
        for col in df_raw.columns:
            print(f"  - {col} (dtype: {df_raw[col].dtype})")

        print("\n" + "=" * 70)
        print("Sample Raw Data (first 3 rows):")
        print("=" * 70)

        # Show a few key columns
        key_cols = ['Id', 'Category', 'Created_at_local', 'Minutes_to_Close']
        display_cols = [col for col in key_cols if col in df_raw.columns]
        print(df_raw[display_cols].head(3))

        # Save raw data
        print("\n" + "=" * 70)
        print("Saving Raw Data:")
        print("=" * 70)
        filepath = api.save_raw_data(df_raw, filename='sample_raw_data.csv')

        print("\n" + "=" * 70)
        print("✓ Raw Data Extraction Complete!")
        print("=" * 70)
        print("\nNote: This is RAW data - no cleaning has been performed.")
        print("Data cleaning will happen in the data_processing pipeline.")
        print("\nNext steps:")
        print("1. Review 'data/raw/sample_raw_data.csv'")
        print("2. Check 'data/raw/sample_raw_data_metadata.json'")
        print("3. Build data cleaning pipeline in data_processing/")

    else:
        print("\nNo records returned")
