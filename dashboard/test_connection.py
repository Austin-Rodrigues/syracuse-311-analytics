"""
Test Databricks connection
"""
from databricks import sql
import pandas as pd

# Your credentials (replace with actual values)
DATABRICKS_HOST = "your-workspace.cloud.databricks.com"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/your-warehouse-id"
DATABRICKS_TOKEN = "dapi..."

print("🔌 Testing Databricks connection...")
print(f"Host: {DATABRICKS_HOST}")
print(f"HTTP Path: {DATABRICKS_HTTP_PATH}")
print(f"Token: {DATABRICKS_TOKEN[:10]}...")

try:
    # Connect
    connection = sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN
    )
    
    print("✅ Connection successful!")
    
    # Test query - list your tables
    cursor = connection.cursor()
    
    print("\n📋 Testing: List all tables in syracuse_project...")
    cursor.execute("SHOW TABLES IN workspace.syracuse_project")
    tables = cursor.fetchall()
    
    print("\n✅ Available tables:")
    for table in tables:
        print(f"  - {table}")
    
    # Test query - check gold table structure
    print("\n📋 Testing: Describe gold_neighborhood_performance...")
    cursor.execute("DESCRIBE workspace.syracuse_project.gold_neighborhood_performance")
    columns = cursor.fetchall()
    
    print("\n✅ Column names in gold_neighborhood_performance:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")
    
    # Test query - fetch sample data
    print("\n📋 Testing: Fetch 5 rows from gold table...")
    cursor.execute("""
        SELECT * 
        FROM workspace.syracuse_project.gold_neighborhood_performance 
        LIMIT 5
    """)
    
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    
    print("\n✅ Sample data:")
    print(df)
    
    print("\n✅ Column names exactly as they appear:")
    print(df.columns.tolist())
    
    cursor.close()
    connection.close()
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your token hasn't expired (regenerate in Databricks)")
    print("2. Verify SQL Warehouse is running (not stopped)")
    print("3. Check http_path is correct (should start with /sql/1.0/warehouses/)")
    print("4. Ensure your token has 'sql' scope")