import os
from dotenv import load_dotenv
from google.cloud import bigquery

def cargar_jsonl_a_bigquery():
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()
    
    # Extraer parámetros de infraestructura de forma segura
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("GCP_DATASET_ID")
    data_dir = os.getenv("DATA_SOURCE_DIR", ".") # Usa el directorio actual por defecto si no existe la variable
    
    if not project_id or not dataset_id:
        raise ValueError("Error: Faltan las variables GCP_PROJECT_ID o GCP_DATASET_ID en el archivo .env")

    # Inicializa el cliente (usa GOOGLE_APPLICATION_CREDENTIALS del .env automáticamente)
    client = bigquery.Client(project=project_id)
    
    # Mapeo de archivos locales a sus respectivas tablas en BigQuery
    archivos_a_cargar = {
            "dim_employees.jsonl": "dim_employees",
            "fact_movements.jsonl": "fact_movements",
            "fact_monthly_payroll.jsonl": "fact_monthly_payroll",
            "fact_absenteeism.jsonl": "fact_absenteeism"
    }
    
    for archivo_local, nombre_tabla in archivos_a_cargar.items():
        # Une la ruta del .env con el nombre del archivo
        ruta_completa = os.path.join(data_dir, archivo_local)
        
        if not os.path.exists(ruta_completa):
            print(f"Advertencia: No se encontró el archivo {ruta_completa}. Saltando...")
            continue
            
        table_id = f"{project_id}.{dataset_id}.{nombre_tabla}"
        
        # Configuración del trabajo de carga en BigQuery
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True 
        )
        
        print(f"Subiendo {archivo_local} a {table_id}...")
        
        with open(ruta_completa, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)
        
        job.result()  
        
        table = client.get_table(table_id)
        print(f"Carga exitosa. La tabla {nombre_tabla} ahora tiene {table.num_rows} filas.\n")

if __name__ == "__main__":
    cargar_jsonl_a_bigquery()