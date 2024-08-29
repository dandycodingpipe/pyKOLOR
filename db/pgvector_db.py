import psycopg2
from psycopg2.extras import execute_values
import pydicom
import numpy as np
from pgvector.psycopg2 import register_vector

class PgVectorDB:
    def __init__(self, dbname, host='localhost', port='5432'):
        # Use 'postgres' as user and 'postgress' as the password
        self.conn = psycopg2.connect(dbname=dbname, user='postgres', password='postgress', host=host, port=port)
        register_vector(self.conn)
        self.cursor = self.conn.cursor()

    def create_medical_image_table(self, table_name, vector_dimension):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            sample_id TEXT,
            body_part_examined TEXT,
            embedding vector({vector_dimension})
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_dicom_with_embedding(self, dicom_path, table_name, embedding):
        dicom = pydicom.dcmread(dicom_path)
        
        # Extract metadata from the DICOM file
        patient_id = dicom.PatientID if 'PatientID' in dicom else None
        study_date = dicom.StudyDate if 'StudyDate' in dicom else None
        modality = dicom.Modality if 'Modality' in dicom else None
        body_part_examined = dicom.BodyPartExamined if 'BodyPartExamined' in dicom else None
        institution_name = dicom.InstitutionName if 'InstitutionName' in dicom else None

        # Convert embedding to list
        embedding_list = embedding.tolist()

        insert_query = f"""
        INSERT INTO {table_name} 
        (patient_id, study_date, modality, body_part_examined, institution_name, embedding)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(insert_query, (
            patient_id, study_date, modality, body_part_examined, institution_name, embedding_list
        ))
        self.conn.commit()

    def create_index(self, table_name, vector_column='embedding', index_type='ivfflat'):
        index_name = f"{table_name}_{vector_column}_idx"
        index_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} USING {index_type} ({vector_column});"
        self.cursor.execute(index_query)
        self.conn.commit()

    def similarity_search(self, table_name, query_vector, top_n=10):
        query_vector_str = f"ARRAY[{', '.join(map(str, query_vector))}]"
        search_query = f"""
        SELECT *, {vector_column} <-> '{query_vector_str}' AS distance
        FROM {table_name}
        ORDER BY distance
        LIMIT {top_n};
        """
        self.cursor.execute(search_query)
        return self.cursor.fetchall()

    def delete_table(self, table_name):
        drop_query = f"DROP TABLE IF EXISTS {table_name};"
        self.cursor.execute(drop_query)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
