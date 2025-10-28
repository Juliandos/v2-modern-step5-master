📘 Guía Técnica Completa: RAG Chat History PDF - LangChain Modern (2025)
🎯 Objetivo
Esta guía te permitirá levantar desde cero el proyecto "Rag-chat-history-pdf-langchain-modern", un sistema RAG (Retrieval-Augmented Generation) moderno con memoria conversacional persistente, basado en el repositorio v2-modern-step5.

📋 Tabla de Contenidos

Requisitos del Sistema
Configuración de Python y Poetry
Creación de Bases de Datos PostgreSQL
Configuración del Entorno (.env)
Instalación de Dependencias
Verificación de Esquemas de Bases de Datos
Carga y Procesamiento de PDFs
Ejecución del Backend
Ejecución del Frontend
Pruebas del Sistema
Verificación de Memoria Conversacional
Solución de Problemas


1. Requisitos del Sistema
Software Necesario

Python 3.13.3
Poetry 2.1.4
PostgreSQL 14+ con extensión pgvector
Node.js 18+ (para el frontend)
Clave OpenAI API


2. Configuración de Python y Poetry
2.1 Instalar pyenv (Gestor de Versiones de Python)
bash# Instalar pyenv (Linux/macOS)
curl https://pyenv.run | bash

# Agregar a ~/.bashrc o ~/.zshrc
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Recargar shell
source ~/.bashrc  # o source ~/.zshrc
2.2 Instalar Python 3.13.3
bash# Instalar Python 3.13.3
pyenv install 3.13.3

# Verificar instalación
pyenv versions
```

**Salida esperada:**
```
  system
* 3.13.3 (set by /home/usuario/.pyenv/version)
2.3 Configurar Python Global
bash# Establecer 3.13.3 como versión global
pyenv global 3.13.3

# Verificar versión activa
python --version
```

**Salida esperada:**
```
Python 3.13.3
2.4 Instalar Poetry con pipx
bash# Instalar pipx si no lo tienes
python -m pip install --user pipx
python -m pipx ensurepath

# Instalar Poetry 2.1.4
pipx install poetry==2.1.4

# Verificar instalación
poetry --version
```

**Salida esperada:**
```
Poetry (version 2.1.4)
2.5 Crear Entorno Virtual del Proyecto
bash# Navegar a la raíz del proyecto
cd /ruta/a/tu/proyecto/rag-chat-history-pdf-langchain-modern

# Crear entorno virtual con pyenv
pyenv virtualenv 3.13.3 rag-step5-env

# Activar el entorno
pyenv activate rag-step5-env

# Verificar entorno activo
pyenv which python
```

**Salida esperada:**
```
/home/usuario/.pyenv/versions/3.13.3/envs/rag-step5-env/bin/python
2.6 Configurar Poetry para Usar el Entorno
bash# Configurar Poetry para usar el entorno actual
poetry env use $(pyenv which python)

# Verificar configuración
poetry env info
```

**Salida esperada:**
```
Virtualenv
Python:         3.13.3
Implementation: CPython
Path:           /home/usuario/.pyenv/versions/3.13.3/envs/rag-step5-env
Executable:     /home/usuario/.pyenv/versions/3.13.3/envs/rag-step5-env/bin/python
Valid:          True

3. Creación de Bases de Datos PostgreSQL
3.1 Conectarse a PostgreSQL
bash# Conectar como usuario postgres
psql -U postgres
```

**Prompt esperado:**
```
psql (16.10 (Ubuntu 16.10-0ubuntu0.24.04.1))
Type "help" for help.

postgres=#
3.2 Crear Base de Datos para Embeddings (database164)
sql-- Crear base de datos principal
CREATE DATABASE database164;

-- Listar bases de datos para verificar
\l | grep database164
```

**Salida esperada:**
```
 database164                   | postgres | UTF8     | libc            | C.UTF-8 | C.UTF-8 |            |           |
3.3 Habilitar Extensión pgvector en database164
sql-- Conectarse a database164
\c database164

-- Crear extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar extensión
\dx
```

**Salida esperada:**
```
                                      List of installed extensions
  Name   | Version |   Schema   |                         Description
---------+---------+------------+--------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vector  | 0.7.0   | public     | vector data type and ivfflat and hnsw access methods
(2 rows)
3.4 Crear Base de Datos para Historial (pdf_rag_history)
sql-- Salir de database164
\c postgres

-- Crear base de datos de historial
CREATE DATABASE pdf_rag_history;

-- Verificar creación
\l | grep pdf_rag_history
```

**Salida esperada:**
```
 pdf_rag_history               | postgres | UTF8     | libc            | C.UTF-8 | C.UTF-8 |            |           |
3.5 Crear Tabla message_store en pdf_rag_history
sql-- Conectarse a pdf_rag_history
\c pdf_rag_history

-- Crear tabla para historial de conversaciones
CREATE TABLE IF NOT EXISTS message_store (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice para búsquedas eficientes
CREATE INDEX IF NOT EXISTS idx_message_store_session_id ON message_store(session_id);

-- Verificar tabla creada
\dt
```

**Salida esperada:**
```
             List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | message_store | table | postgres
(1 row)
3.6 Salir de PostgreSQL
sql-- Salir de psql
\q

4. Configuración del Entorno (.env)
4.1 Copiar Template
bash# Desde la raíz del proyecto
cp .env.template .env
4.2 Editar Archivo .env
bashnano .env  # o usa tu editor preferido
Contenido del archivo .env:
bash# OpenAI Configuration
OPENAI_API_KEY=sk-proj-TU_CLAVE_OPENAI_AQUI

# Database Configuration - Embeddings
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/database164

# Database Configuration - Chat History
DATABASE_URL_UNO=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/pdf_rag_history

# LangSmith Configuration (Opcional - para monitoreo)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_TU_CLAVE_LANGSMITH
LANGCHAIN_PROJECT=rag-chat-history-project
⚠️ Importante: Reemplaza TU_CLAVE_OPENAI_AQUI, TU_PASSWORD y TU_CLAVE_LANGSMITH con tus valores reales.
4.3 Verificar Formato de URLs
bash# Verificar que las URLs estén correctas
cat .env | grep DATABASE
```

**Salida esperada:**
```
DATABASE_URL=postgresql+psycopg://postgres:tu_password@localhost:5432/database164
DATABASE_URL_UNO=postgresql+psycopg://postgres:tu_password@localhost:5432/pdf_rag_history

5. Instalación de Dependencias
5.1 Backend - Instalar con Poetry
bash# Asegurarse de estar en la raíz del proyecto
cd /ruta/a/tu/proyecto/rag-chat-history-pdf-langchain-modern

# Asegurarse de que el entorno virtual está activado
pyenv activate rag-step5-env

# Instalar dependencias del backend
poetry install
```

**Salida esperada (parcial):**
```
Installing dependencies from lock file

Package operations: 150 installs, 0 updates, 0 removals

  - Installing certifi (2024.x.x)
  - Installing charset-normalizer (3.x.x)
  ...
  - Installing fastapi (0.115.0)
  - Installing langchain-core (0.3.0)
  - Installing langchain-openai (0.2.0)
  - Installing psycopg2-binary (2.9.11)
  ...

Installing the current project: v2-modern-step5 (5.0.0)
5.2 Verificar Instalación de Dependencias
bash# Verificar paquetes instalados
poetry show | grep -E "fastapi|langchain|psycopg"
```

**Salida esperada:**
```
fastapi                   0.115.0
langchain-community       0.3.0
langchain-core            0.3.0
langchain-experimental    0.3.0
langchain-openai          0.2.0
psycopg                   3.2.0
psycopg2-binary           2.9.11
5.3 Frontend - Instalar con npm
bash# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install
```

**Salida esperada (parcial):**
```
added 1500 packages, and audited 1501 packages in 45s

250 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
5.4 Verificar Instalación del Frontend
bash# Verificar paquetes clave
npm list react react-dom uuid @microsoft/fetch-event-source tailwindcss
```

**Salida esperada:**
```
modern-rag-frontend-step5@0.1.0
├── @microsoft/fetch-event-source@2.0.1
├── react-dom@19.0.0
├── react@19.0.0
├── tailwindcss@3.4.18
└── uuid@10.0.0

6. Verificación de Esquemas de Bases de Datos
6.1 Verificar Esquema de pdf_rag_history
bash# Conectarse a la base de datos
psql -U postgres -d pdf_rag_history
```

**Prompt esperado:**
```
Password for user postgres:
psql (16.10 (Ubuntu 16.10-0ubuntu0.24.04.1))
Type "help" for help.

pdf_rag_history=#
Verificar tablas:
sql\dt
```

**Salida esperada:**
```
             List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | message_store | table | postgres
(1 row)
Verificar estructura de message_store:
sql\d message_store
```

**Salida esperada:**
```
                              Table "public.message_store"
   Column   |            Type             | Collation | Nullable |                  Default
------------+-----------------------------+-----------+----------+-------------------------------------------
 id         | integer                     |           | not null | nextval('message_store_id_seq'::regclass)
 session_id | text                        |           |          |
 message    | jsonb                       |           |          |
 created_at | timestamp without time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "message_store_pkey" PRIMARY KEY, btree (id)
    "idx_message_store_session_id" btree (session_id)
Verificar columnas detalladamente:
sqlSELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

**Salida esperada:**
```
  table_name   | column_name |          data_type
---------------+-------------+-----------------------------
 message_store | id          | integer
 message_store | session_id  | text
 message_store | message     | jsonb
 message_store | created_at  | timestamp without time zone
(4 rows)
Salir:
sql\q
6.2 Verificar Esquema de database164
bash# Conectarse a database164
psql -U postgres -d database164
Verificar tablas:
sql\dt
```

**Salida esperada (antes de cargar PDFs):**
```
Did not find any relations.
```

**O después de cargar PDFs:**
```
             List of relations
 Schema |          Name           | Type  |  Owner
--------+-------------------------+-------+----------
 public | langchain_pg_collection | table | postgres
 public | langchain_pg_embedding  | table | postgres
(2 rows)
Verificar estructura de langchain_pg_collection:
sql\d langchain_pg_collection
```

**Salida esperada:**
```
            Table "public.langchain_pg_collection"
  Column   |       Type        | Collation | Nullable | Default
-----------+-------------------+-----------+----------+---------
 name      | character varying |           |          |
 cmetadata | json              |           |          |
 uuid      | uuid              |           | not null |
Indexes:
    "langchain_pg_collection_pkey" PRIMARY KEY, btree (uuid)
Referenced by:
    TABLE "langchain_pg_embedding" CONSTRAINT "langchain_pg_embedding_collection_id_fkey" FOREIGN KEY (collection_id) REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE
Verificar estructura de langchain_pg_embedding:
sql\d langchain_pg_embedding
```

**Salida esperada:**
```
            Table "public.langchain_pg_embedding"
    Column     |       Type        | Collation | Nullable | Default
---------------+-------------------+-----------+----------+---------
 collection_id | uuid              |           |          |
 embedding     | vector            |           |          |
 document      | character varying |           |          |
 cmetadata     | json              |           |          |
 custom_id     | character varying |           |          |
 uuid          | uuid              |           | not null |
Indexes:
    "langchain_pg_embedding_pkey" PRIMARY KEY, btree (uuid)
Foreign-key constraints:
    "langchain_pg_embedding_collection_id_fkey" FOREIGN KEY (collection_id) REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE
Salir:
sql\q

7. Carga y Procesamiento de PDFs
7.1 Colocar PDFs en el Directorio
bash# Crear directorio si no existe
mkdir -p pdf-documents

# Copiar tus PDFs al directorio
cp /ruta/a/tus/pdfs/*.pdf pdf-documents/

# Verificar PDFs copiados
ls -lh pdf-documents/
```

**Salida esperada:**
```
total 5.2M
-rw-r--r-- 1 usuario usuario 1.2M oct 27 10:00 John_F_Kennedy.pdf
-rw-r--r-- 1 usuario usuario 850K oct 27 10:00 Robert_F_Kennedy.pdf
-rw-r--r-- 1 usuario usuario 3.1M oct 27 10:00 Joseph_P_Kennedy_Sr.pdf
7.2 Ejecutar Script de Procesamiento
bash# Desde la raíz del proyecto
poetry run python rag-data-loader/rag_load_and_process.py
```

**Salida esperada:**
```
Loading documents: 100%|██████████| 3/3 [00:02<00:00,  1.2it/s]
Created 167 chunks from 79 documents
Vector database created successfully!
7.3 Verificar Datos Cargados en la Base de Datos
bash# Conectarse a database164
psql -U postgres -d database164

# Verificar colección creada
SELECT name, uuid FROM langchain_pg_collection;
```

**Salida esperada:**
```
       name       |                 uuid
------------------+--------------------------------------
 collection164    | 12345678-1234-1234-1234-123456789abc
(1 row)
Verificar embeddings:
sqlSELECT COUNT(*) as total_embeddings FROM langchain_pg_embedding;
```

**Salida esperada:**
```
 total_embeddings
------------------
              167
(1 row)
Ver muestra de documentos:
sqlSELECT LEFT(document, 100) as document_preview, cmetadata->>'source' as source
FROM langchain_pg_embedding
LIMIT 3;
```

**Salida esperada:**
```
                                          document_preview                                         |                              source
----------------------------------------------------------------------------------------------------+------------------------------------------------------------------
 John Fitzgerald Kennedy (May 29, 1917 – November 22, 1963), often referred to by his initials... | /ruta/completa/pdf-documents/John_F_Kennedy.pdf
 Kennedy was the youngest person elected president, and the youngest president at the end of... | /ruta/completa/pdf-documents/John_F_Kennedy.pdf
 Robert Francis Kennedy (November 20, 1925 – June 6, 1968), also known as RFK, was an American... | /ruta/completa/pdf-documents/Robert_F_Kennedy.pdf
(3 rows)
Salir:
sql\q

8. Ejecución del Backend
8.1 Iniciar Servidor Backend
bash# Desde la raíz del proyecto
# Asegurarse de que el entorno virtual está activado
pyenv activate rag-step5-env

# Iniciar servidor con hot-reload
poetry run uvicorn app.server:app --reload --port 8000
```

**Salida esperada:**
```
INFO:     Will watch for changes in these directories: ['/ruta/proyecto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
8.2 Verificar Salud del Backend
bash# En otra terminal
curl http://localhost:8000/health
Salida esperada:
json{"status":"healthy","version":"5.0.0"}
```

### 8.3 Verificar Documentación API

Abrir en el navegador:
```
http://localhost:8000/docs
Deberías ver:

Interfaz Swagger UI
Endpoints disponibles: /query, /stream, /upload, /load-and-process-pdfs, /health
Posibilidad de probar endpoints directamente


9. Ejecución del Frontend
9.1 Iniciar Servidor Frontend
bash# En una nueva terminal, navegar al frontend
cd frontend

# Iniciar servidor de desarrollo
npm start
```

**Salida esperada:**
```
Compiled successfully!

You can now view modern-rag-frontend-step5 in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

### 9.2 Verificar Frontend en el Navegador

Abrir en el navegador:
```
http://localhost:3000
```

**Deberías ver:**
- Interfaz de chat moderna
- Header: "A Modern CHAT WITH YOUR PRIVATE PDFS RAG LLM App (2025)"
- Área de mensajes vacía con texto: "Ask a question about your PDF documents to get started!"
- Campo de texto para preguntas
- Botón "Send"
- Sección de carga de archivos PDF

---

## 10. Pruebas del Sistema

### 10.1 Prueba Básica de Consulta

**En el navegador (http://localhost:3000):**

1. **Escribe en el campo de texto:**
```
   ¿Quién es JFK?
```

2. **Presiona Enter o click en "Send"**

**Comportamiento esperado:**
- Mensaje del usuario aparece en azul claro
- Respuesta del AI aparece palabra por palabra (streaming)
- Al final, aparecen las fuentes con enlaces clickeables

**Salida del backend (terminal):**
```
🔄 Using stream WITH history (session: cbecb465-9fba-42ca-a432-c0f12179b9f8)
============================================================
🎯 Streaming with history
📝 Session ID: cbecb465-9fba-42ca-a432-c0f12179b9f8
❓ Question: ¿Quién es JFK?
📜 Loaded 0 messages from history for session cbecb465-9fba-42ca-a432-c0f12179b9f8
🔍 No history, using original question
✨ Final question for streaming: ¿Quién es JFK?
💾 Saved conversation to history for session cbecb465-9fba-42ca-a432-c0f12179b9f8
✅ Verification: Now have 2 messages in history
💾 Saved streamed conversation
============================================================
INFO:     127.0.0.1:41560 - "POST /stream HTTP/1.1" 200 OK
10.2 Prueba con curl (Opcional)
bash# Prueba de consulta simple
curl -X POST "http://localhost:8000/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Quién es JFK?",
    "config": {
      "configurable": {
        "session_id": "test-session-123"
      }
    }
  }'
```

**Salida esperada (parcial):**
```
data: {"chunk": {"docs": ["John_F_Kennedy.pdf", "John_F_Kennedy.pdf", ...]}}

data: {"chunk": {"answer": ""}}

data: {"chunk": {"answer": "John"}}

data: {"chunk": {"answer": " F"}}

data: {"chunk": {"answer": "."}}

...

data: [DONE]
```

---

## 11. Verificación de Memoria Conversacional

### 11.1 Prueba de Conversación Secuencial

**Pregunta 1:**
```
¿Quién es JFK?
```

**Respuesta esperada:**
```
John Fitzgerald Kennedy, comúnmente conocido como JFK, fue el 35º presidente 
de los Estados Unidos desde 1961 hasta su asesinato en 1963...
```

**Pregunta 2 (pregunta meta-conversacional):**
```
¿Qué te pregunté antes?
```

**Respuesta esperada:**
```
Tu pregunta anterior fue: "¿Quién es JFK?"
```

**Salida del backend:**
```
🔄 Using stream WITH history (session: cbecb465-9fba-42ca-a432-c0f12179b9f8)
============================================================
🎯 Streaming with history
📝 Session ID: cbecb465-9fba-42ca-a432-c0f12179b9f8
❓ Question: ¿Qué te pregunté antes?
📜 Loaded 2 messages from history for session cbecb465-9fba-42ca-a432-c0f12179b9f8
  Message 1: HumanMessage - ¿Quién es JFK?
  Message 2: AIMessage - John Fitzgerald Kennedy, comúnmente conocido como ...
🔎 Checking if meta-question: '¿qué te pregunté antes?' -> True
🔍 Meta-question detected! Answering from conversation history directly
✨ Direct answer from history: Tu pregunta anterior fue: "¿Quién es JFK?"
💾 Saved meta-conversation
============================================================
```

**Pregunta 3 (pregunta contextual):**
```
¿Cuándo nació él?
```

**Respuesta esperada:**
```
John F. Kennedy nació el 29 de mayo de 1917.
```

**Salida del backend:**
```
📜 Loaded 4 messages from history for session cbecb465-9fba-42ca-a432-c0f12179b9f8
  Message 1: HumanMessage - ¿Quién es JFK?
  Message 2: AIMessage - John Fitzgerald Kennedy...
  Message 3: HumanMessage - ¿Qué te pregunté antes?
  Message 4: AIMessage - Tu pregunta anterior fue...
🔍 Generating standalone question with 4 recent messages
🔍 Standalone question: ¿Cuándo nació John F. Kennedy?
✨ Final question for streaming: ¿Cuándo nació John F. Kennedy?
11.2 Verificar Historial en la Base de Datos
bash# Conectarse a pdf_rag_history
psql -U postgres -d pdf_rag_history

# Ver conversaciones guardadas
SELECT 
    session_id,
    message->'data'->>'type' as type,
    LEFT(message->'data'->>'content', 60) as content,
    created_at
FROM message_store
ORDER BY created_at DESC
LIMIT 10;
```

**Salida esperada:**
```
           session_id           | type  |                           content                            |         created_at
--------------------------------+-------+--------------------------------------------------------------+----------------------------
 cbecb465-9fba-42ca-a432-c0f... | ai    | John F. Kennedy nació el 29 de mayo de 1917.                 | 2025-10-27 16:35:20.123456
 cbecb465-9fba-42ca-a432-c0f... | human | ¿Cuándo nació él?                                            | 2025-10-27 16:35:15.654321
 cbecb465-9fba-42ca-a432-c0f... | ai    | Tu pregunta anterior fue: "¿Quién es JFK?"                   | 2025-10-27 16:34:50.987654
 cbecb465-9fba-42ca-a432-c0f... | human | ¿Qué te pregunté antes?                                      | 2025-10-27 16:34:45.321098
 cbecb465-9fba-42ca-a432-c0f... | ai    | John Fitzgerald Kennedy, comúnmente conocido como JFK, fue.. | 2025-10-27 16:34:10.654321
 cbecb465-9fba-42ca-a432-c0f... | human | ¿Quién es JFK?                                               | 2025-10-27 16:34:05.123456
(6 rows)
Salir:
sql\q
```

---

## 12. Solución de Problemas

### 12.1 Error: "Module 'psycopg2' not found"

**Problema:**
```
ModuleNotFoundError: No module named 'psycopg2'
Solución:
bashpoetry add psycopg2-binary
12.2 Error: "Connection refused" al Conectar con PostgreSQL
Verificar que PostgreSQL está corriendo:
bashsudo systemctl status postgresql
Si no está corriendo:
bashsudo systemctl start postgresql
12.3 Error: "Extension 'vector' does not exist"
Instalar pgvector:
bash# Ubuntu/Debian
sudo apt install postgresql-16-pgvector

# Verificar instalación
psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
12.4 Frontend No Se Conecta al Backend (CORS)
Verificar configuración CORS en app/server.py:
pythonapp.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
12.5 Error: "OPENAI_API_KEY not set"
Verificar archivo .env:
bashcat .env | grep OPENAI_API_KEY
Si no está configurada:
bashecho "OPENAI_API_KEY=sk-proj-TU_CLAVE_AQUI" >> .env
12.6 No Se Guardan Conversaciones en la DB
Verificar conexión a pdf_rag_history:
bashpsql -U postgres -d pdf_rag_history -c "SELECT COUNT(*) FROM message_store;"
Si la tabla no existe:
sql-- Volver a ejecutar la creación de tabla (Sección 3.5)
CREATE TABLE IF NOT EXISTS message_store (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

🎉 ¡Listo!
Tu sistema RAG con memoria conversacional ahora está completamente funcional. Puedes:
✅ Hacer preguntas sobre tus PDFs
✅ El sistema recuerda conversaciones previas
✅ Detecta preguntas meta-conversacionales ("¿qué te pregunté antes?")
✅ Genera preguntas standalone para consultas contextuales
✅ Streaming en tiempo real de respuestas
✅ Citar fuentes con enlaces a PDFs originales

📊 Anexo A: Comandos de Verificación Rápida
A.1 Verificación Completa del Sistema
bash#!/bin/bash
# Script de verificación rápida del sistema

echo "=== Verificación del Sistema RAG ==="
echo ""

echo "1. Verificando Python..."
python --version

echo ""
echo "2. Verificando Poetry..."
poetry --version

echo ""
echo "3. Verificando entorno virtual..."
poetry env info

echo ""
echo "4. Verificando PostgreSQL..."
psql -U postgres -c "SELECT version();" 2>/dev/null && echo "✅ PostgreSQL funcionando" || echo "❌ PostgreSQL no responde"

echo ""
echo "5. Verificando bases de datos..."
psql -U postgres -l | grep -E "database164|pdf_rag_history"

echo ""
echo "6. Verificando backend..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend funcionando" || echo "❌ Backend no responde"

echo ""
echo "7. Verificando frontend..."
curl -s http://localhost:3000 | grep -q "Modern RAG" && echo "✅ Frontend funcionando" || echo "❌ Frontend no responde"

echo ""
echo "=== Verificación Completada ==="
Guardar como verify_system.sh y ejecutar:
bashchmod +x verify_system.sh
./verify_system.sh
A.2 Comandos Útiles para Desarrollo
bash# Ver logs del backend en tiempo real
tail -f logs/backend.log  # Si tienes logs configurados

# Reiniciar backend rápidamente
pkill -f uvicorn && poetry run uvicorn app.server:app --reload --port 8000

# Limpiar historial de conversaciones
psql -U postgres -d pdf_rag_history -c "TRUNCATE TABLE message_store;"

# Ver últimas 10 conversaciones
psql -U postgres -d pdf_rag_history -c "
SELECT 
    session_id,
    message->'data'->>'type' as type,
    LEFT(message->'data'->>'content', 50) as content,
    created_at
FROM message_store
ORDER BY created_at DESC
LIMIT 10;
"

# Contar embeddings en database164
psql -U postgres -d database164 -c "SELECT COUNT(*) FROM langchain_pg_embedding;"

# Ver colecciones disponibles
psql -U postgres -d database164 -c "SELECT name, uuid FROM langchain_pg_collection;"

📊 Anexo B: Estructura de Datos
B.1 Formato de Mensajes en message_store
Mensaje Humano:
json{
  "type": "human",
  "data": {
    "content": "¿Quién es JFK?",
    "type": "human"
  }
}
Mensaje AI:
json{
  "type": "ai",
  "data": {
    "content": "John Fitzgerald Kennedy, comúnmente conocido como JFK...",
    "type": "ai"
  }
}
B.2 Formato de Session ID
El frontend genera automáticamente un UUID v4 para cada sesión:
typescript// frontend/src/App.tsx
const sessionIdRef = useRef<string>(uuidv4());

// Ejemplo de session_id generado:
// "cbecb465-9fba-42ca-a432-c0f12179b9f8"
B.3 Estructura de Embeddings
sql-- Ver estructura de un embedding
SELECT 
    uuid,
    collection_id,
    LEFT(document, 100) as doc_preview,
    cmetadata,
    custom_id,
    array_length(embedding, 1) as embedding_dimensions
FROM langchain_pg_embedding
LIMIT 1;
```

**Salida esperada:**
```
                 uuid                 |            collection_id             |                                           doc_preview                                            |                      cmetadata                       | custom_id | embedding_dimensions
--------------------------------------+--------------------------------------+--------------------------------------------------------------------------------------------------+------------------------------------------------------+-----------+----------------------
 123e4567-e89b-12d3-a456-426614174000 | 987f6543-e21a-43b1-c234-567890abcdef | John Fitzgerald Kennedy (May 29, 1917 – November 22, 1963), often referred to by his initials... | {"source": "/path/to/John_F_Kennedy.pdf"}            |           |                 1536
```

---

## 📊 Anexo C: Flujo de Datos del Sistema

### C.1 Flujo de una Consulta Simple (Sin Historial)
```
Usuario → Frontend (React)
    ↓
    ├─ Genera session_id (UUID)
    ├─ Envía POST /stream con question + config
    ↓
Backend (FastAPI)
    ↓
    ├─ Recibe request con session_id
    ├─ get_chat_history(session_id) → 0 mensajes
    ├─ No genera standalone question
    ├─ MultiQueryRetriever genera 3 variaciones
    │   ├─ Variación 1: "Who is JFK?"
    │   ├─ Variación 2: "Tell me about John F. Kennedy"
    │   └─ Variación 3: "What do you know about President Kennedy?"
    ├─ Vector search en database164 (3 búsquedas)
    ├─ Combina documentos únicos
    ├─ Genera respuesta con LLM (streaming)
    ├─ save_to_chat_history() → Guarda en pdf_rag_history
    ↓
Frontend
    ↓
    └─ Muestra respuesta palabra por palabra + fuentes
```

### C.2 Flujo de una Consulta Contextual (Con Historial)
```
Usuario → Frontend (React)
    ↓
    ├─ Usa mismo session_id de conversación anterior
    ├─ Envía "¿Cuándo nació él?" con session_id
    ↓
Backend (FastAPI)
    ↓
    ├─ get_chat_history(session_id) → 2 mensajes
    │   ├─ Message 1: HumanMessage("¿Quién es JFK?")
    │   └─ Message 2: AIMessage("John F. Kennedy fue...")
    ├─ generate_standalone_question()
    │   ├─ Input: "¿Cuándo nació él?" + chat_history
    │   ├─ LLM reformula contexto
    │   └─ Output: "¿Cuándo nació John F. Kennedy?"
    ├─ MultiQueryRetriever con pregunta standalone
    ├─ Vector search con mejor contexto
    ├─ Genera respuesta precisa
    ├─ save_to_chat_history() → Ahora 4 mensajes en DB
    ↓
Frontend
    ↓
    └─ Muestra respuesta contextualizada + fuentes
```

### C.3 Flujo de una Pregunta Meta-Conversacional
```
Usuario → Frontend
    ↓
    └─ "¿Qué te pregunté antes?"
    ↓
Backend
    ↓
    ├─ get_chat_history(session_id) → 2+ mensajes
    ├─ Detecta keywords meta-conversacionales
    │   └─ "qué te pregunté", "pregunta anterior", etc.
    ├─ Extrae preguntas humanas del historial
    ├─ NO consulta vector database (ahorro de recursos)
    ├─ Responde directamente: "Tu pregunta anterior fue: '...'"
    ├─ save_to_chat_history()
    ↓
Frontend
    ↓
    └─ Muestra respuesta inmediata sin fuentes

📊 Anexo D: Monitoreo con LangSmith (Opcional)
D.1 Configurar LangSmith
bash# Ya configurado en .env:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_TU_CLAVE
LANGCHAIN_PROJECT=rag-chat-history-project
```

### D.2 Ver Trazas en LangSmith

1. **Acceder a LangSmith:** https://smith.langchain.com
2. **Navegar a tu proyecto:** `rag-chat-history-project`
3. **Observar trazas en tiempo real:**

**Ejemplo de traza MultiQuery:**
```
📊 Trace: "¿Quién es JFK?"
  ├─ 🔄 RunnableWithMessageHistory
  │   ├─ 📜 Load chat history (0 messages)
  │   ├─ 🔍 MultiQueryRetriever
  │   │   ├─ 🤖 LLM Query Generation (gpt-4o-mini)
  │   │   │   └─ Generated 3 queries
  │   │   ├─ 🔎 Vector Search 1 → 4 docs
  │   │   ├─ 🔎 Vector Search 2 → 3 docs
  │   │   └─ 🔎 Vector Search 3 → 5 docs
  │   ├─ 📋 Combined: 8 unique docs
  │   └─ 🤖 Answer Generation (gpt-4o-mini)
  └─ 💾 Save to history
D.3 Métricas Observables

Latencia total: Tiempo desde pregunta hasta respuesta completa
Tiempo de carga de historial: Velocidad de consulta a PostgreSQL
Tokens usados: Input y output tokens por consulta
Costo estimado: Basado en tokens y modelo usado
Documentos recuperados: Cantidad y fuentes


📊 Anexo E: Optimizaciones Avanzadas
E.1 Limitar Historial de Conversación
Si las conversaciones se vuelven muy largas, puedes limitar el historial:
En app/rag_chain.py:
pythondef generate_standalone_question(question: str, chat_history: List) -> str:
    # Ya implementado: limita a últimos 6 mensajes (3 intercambios)
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
    history_text = get_buffer_string(recent_history)
    # ... resto del código
E.2 Política de Expiración de Sesiones
Limpiar sesiones antiguas (ejecutar periódicamente):
sql-- Eliminar sesiones más antiguas de 7 días
DELETE FROM message_store
WHERE created_at < NOW() - INTERVAL '7 days';
O crear un cron job:
bash# Agregar a crontab (ejecutar diariamente a las 2 AM)
0 2 * * * psql -U postgres -d pdf_rag_history -c "DELETE FROM message_store WHERE created_at < NOW() - INTERVAL '7 days';" >> /var/log/cleanup_sessions.log 2>&1
E.3 Índices Adicionales para Mejor Performance
sql-- Conectarse a pdf_rag_history
\c pdf_rag_history

-- Índice compuesto para búsquedas por sesión y fecha
CREATE INDEX IF NOT EXISTS idx_message_store_session_created 
ON message_store(session_id, created_at DESC);

-- Índice para limpiezas por fecha
CREATE INDEX IF NOT EXISTS idx_message_store_created_at 
ON message_store(created_at);

-- Verificar índices
\d message_store
E.4 Configurar Pool de Conexiones PostgreSQL
En app/rag_chain.py, optimizar el engine:
pythonfrom sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

history_engine = create_engine(
    postgres_memory_url,
    poolclass=QueuePool,
    pool_size=5,          # Número de conexiones permanentes
    max_overflow=10,      # Conexiones adicionales en picos
    pool_pre_ping=True,   # Verificar conexiones antes de usar
    pool_recycle=3600     # Reciclar conexiones cada hora
)

📊 Anexo F: Testing Automatizado
F.1 Test de Conexión a Bases de Datos
Crear tests/test_database.py:
pythonimport pytest
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def test_database164_connection():
    """Verificar conexión a database164"""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_pdf_rag_history_connection():
    """Verificar conexión a pdf_rag_history"""
    engine = create_engine(os.getenv("DATABASE_URL_UNO"))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_message_store_table_exists():
    """Verificar que tabla message_store existe"""
    engine = create_engine(os.getenv("DATABASE_URL_UNO"))
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'message_store')"
        ))
        assert result.scalar() is True

def test_pgvector_extension():
    """Verificar extensión pgvector instalada"""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        ))
        assert result.scalar() is True
Ejecutar tests:
bashpoetry run pytest tests/test_database.py -v
```

**Salida esperada:**
```
tests/test_database.py::test_database164_connection PASSED           [ 25%]
tests/test_database.py::test_pdf_rag_history_connection PASSED       [ 50%]
tests/test_database.py::test_message_store_table_exists PASSED       [ 75%]
tests/test_database.py::test_pgvector_extension PASSED               [100%]

============================== 4 passed in 0.45s ===============================
F.2 Test de Endpoints del Backend
Crear tests/test_api.py:
pythonimport pytest
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_health_endpoint():
    """Verificar endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "5.0.0"}

def test_query_endpoint():
    """Verificar endpoint de consulta"""
    response = client.post(
        "/query",
        json={
            "question": "test question",
            "config": {}
        }
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "docs" in response.json()

def test_stream_endpoint():
    """Verificar endpoint de streaming"""
    response = client.post(
        "/stream",
        json={
            "question": "test question",
            "config": {
                "configurable": {
                    "session_id": "test-session"
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
Ejecutar tests:
bashpoetry run pytest tests/test_api.py -v

📊 Anexo G: Despliegue en Producción (Recomendaciones)
G.1 Variables de Entorno para Producción
Crear .env.production:
bash# Production Configuration
OPENAI_API_KEY=sk-prod-...

# Production Database URLs (usar servicios gestionados)
DATABASE_URL=postgresql+psycopg://user:pass@prod-db.example.com:5432/database164
DATABASE_URL_UNO=postgresql+psycopg://user:pass@prod-db.example.com:5432/pdf_rag_history

# LangSmith Production
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=rag-production

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
G.2 Dockerfile para Backend
Crear Dockerfile:
dockerfileFROM python:3.13.3-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==2.1.4

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
G.3 docker-compose.yml
Crear docker-compose.yml:
yamlversion: '3.8'

services:
  postgres:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_URL_UNO=${DATABASE_URL_UNO}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./pdf-documents:/app/pdf-documents

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:8000

volumes:
  postgres_data:
G.4 Nginx como Reverse Proxy
Crear nginx.conf:
nginxupstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # Static files
    location /static/ {
        proxy_pass http://backend/static/;
    }
}
```

---

## 🎓 Anexo H: Conceptos Clave del Sistema

### H.1 ¿Qué es RAG (Retrieval-Augmented Generation)?

**RAG** combina:
1. **Retrieval (Recuperación):** Buscar documentos relevantes en una base de datos vectorial
2. **Augmented (Aumentado):** Enriquecer el prompt del LLM con contexto de documentos
3. **Generation (Generación):** LLM genera respuesta basada en contexto recuperado

**Ventajas:**
- ✅ Respuestas basadas en tus documentos específicos
- ✅ Información actualizable sin reentrenar el modelo
- ✅ Citas de fuentes verificables
- ✅ Menor alucinación del LLM

### H.2 ¿Qué es MultiQuery Retrieval?

**Problema:** Una sola pregunta puede no encontrar todos los documentos relevantes.

**Solución MultiQuery:**
1. Genera 3 variaciones de la pregunta original
2. Ejecuta búsqueda vectorial para cada variación
3. Combina resultados únicos
4. Mejora recall (recuperación) en 40-60%

**Ejemplo:**
```
Pregunta original: "¿Cómo resetear mi contraseña?"

MultiQuery genera:
1. "¿Cómo resetear mi contraseña?"
2. "¿Qué pasos seguir para cambiar mi clave de acceso?"
3. "¿Cómo recuperar mi cuenta si olvidé mi password?"

→ Más documentos relevantes encontrados
```

### H.3 ¿Qué es Standalone Question Generation?

**Problema:** Preguntas de seguimiento carecen de contexto.

**Ejemplo:**
```
Usuario: "¿Quién es JFK?"
AI: "John F. Kennedy fue el 35º presidente..."
Usuario: "¿Cuándo nació él?"  ← "él" no tiene sentido sin contexto
Solución:
python# El sistema reformula basándose en historial:
"¿Cuándo nació él?" + historial
    ↓
"¿Cuándo nació John F. Kennedy?"  ← Pregunta standalone
```

### H.4 ¿Qué son los Embeddings?

**Embeddings** son representaciones numéricas (vectores) de texto que capturan significado semántico.

**Ejemplo:**
```
Texto: "John F. Kennedy was president"
    ↓ (OpenAI text-embedding-3-small)
Vector: [0.023, -0.154, 0.892, ..., 0.234]  (1536 dimensiones)
```

**Similitud semántica:**
```
"JFK was president" ≈ "Kennedy served as POTUS"
(vectores cercanos en espacio 1536D)
H.5 ¿Qué es pgvector?
pgvector es una extensión de PostgreSQL para:

Almacenar vectores de alta dimensión
Realizar búsquedas de similitud eficientes
Usar índices IVFFlat o HNSW para rapidez

Operaciones:
sql-- Buscar los 5 documentos más similares
SELECT document, embedding <-> query_vector AS distance
FROM langchain_pg_embedding
ORDER BY distance
LIMIT 5;

🔐 Anexo I: Seguridad y Mejores Prácticas
I.1 Proteger Claves API
❌ Nunca hacer:
python# NO hard-codear claves
OPENAI_API_KEY = "sk-proj-abc123..."
✅ Siempre usar:
python# Usar variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
I.2 Sanitizar Inputs del Usuario
En app/server.py, agregar validación:
pythonfrom pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    question: str
    config: dict = {}
    
    @validator('question')
    def validate_question(cls, v):
        # Limitar longitud
        if len(v) > 1000:
            raise ValueError('Question too long (max 1000 chars)')
        
        # Eliminar caracteres peligrosos
        if any(char in v for char in ['<', '>', ';', '|']):
            raise ValueError('Invalid characters in question')
        
        return v.strip()
I.3 Rate Limiting
Instalar dependencia:
bashpoetry add slowapi
Configurar en app/server.py:
pythonfrom slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/stream")
@limiter.limit("10/minute")  # Máximo 10 requests por minuto
async def stream_query(request: Request, query: QueryRequest):
    # ... código existente
I.4 Logging Seguro
Configurar logging sin exponer datos sensibles:
pythonimport logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# NO loguear datos sensibles
logger.info(f"Processing query for session: {session_id[:8]}...")  # Solo primeros 8 chars

📚 Anexo J: Recursos Adicionales
J.1 Documentación Oficial

LangChain: https://docs.langchain.com
FastAPI: https://fastapi.tiangolo.com
PostgreSQL: https://www.postgresql.org/docs/
pgvector: https://github.com/pgvector/pgvector
React 19: https://react.dev
OpenAI API: https://platform.openai.com/docs

J.2 Tutoriales Recomendados

LangChain Chat History: https://python.langchain.com/docs/modules/memory/
MultiQuery Retriever: https://python.langchain.com/docs/modules/data_connection/retrievers/MultiQueryRetriever
Server-Sent Events: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

J.3 Comunidades

LangChain Discord: https://discord.gg/langchain
FastAPI Discord: https://discord.gg/fastapi
PostgreSQL Mailing Lists: https://www.postgresql.org/list/


✅ Checklist Final de Verificación
Antes de considerar el sistema completamente funcional, verifica:
Backend:

 Python 3.13.3 instalado y activo
 Poetry 2.1.4 instalado
 Entorno virtual rag-step5-env creado y activado
 Dependencias instaladas con poetry install
 Archivo .env configurado correctamente
 PostgreSQL corriendo
 Base de datos database164 creada con extensión vector
 Base de datos pdf_rag_history creada
 Tabla message_store creada con índices
 PDFs procesados y cargados en database164
 Backend iniciado en http://localhost:8000
 Endpoint /health responde correctamente

Frontend:

 Node.js 18+ instalado
 Dependencias instaladas con npm install
 Frontend iniciado en http://localhost:3000
 Interfaz de chat visible en navegador

Funcionalidad:

 Consulta simple funciona ("¿Quién es JFK?")
 Respuesta streaming funciona (palabra por palabra)
 Fuentes aparecen con enlaces clickeables
 Preguntas meta-conversacionales funcionan ("¿Qué te pregunté antes?")
 Preguntas contextuales funcionan ("¿Cuándo nació él?")
 Historial se guarda en pdf_rag_history
 Session ID se mantiene durante conversación
 Nueva pestaña = nueva conversación


🎉 ¡Felicidades!
Has completado exitosamente la configuración y puesta en marcha del sistema RAG Chat History PDF - LangChain Modern.
Tu sistema ahora incluye:

✅ Recuperación aumentada (RAG) con MultiQuery
✅ Memoria conversacional persistente en PostgreSQL
✅ Detección de preguntas meta-conversacionales
✅ Generación de preguntas standalone
✅ Streaming en tiempo real
✅ Citación de fuentes
✅ Arquitectura moderna 2025

Siguiente nivel:

Agregar autenticación de usuarios
Implementar múltiples colecciones de documentos
Agregar funcionalidad de subida de PDFs desde UI
Desplegar en producción
Agregar analytics y monitoreo

¿Preguntas o problemas? Revisa la sección de Solución de Problemas (Sección 12) o los tests automatizados (Anexo F).

Documento creado: Octubre 2025
Versión del sistema: 5.0.0
Basado en: v2-modern-step5
Python: 3.13.3 | Poetry: 2.1.4 | PostgreSQL: 14+ | React: 19.0.0